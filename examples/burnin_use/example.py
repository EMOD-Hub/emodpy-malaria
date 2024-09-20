#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder

# emodpy
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy_malaria.reporters.builtin import *

import manifest


"""
This example downloads serialized files from the burnin/example
The important bits are in set_param_fn function and general_sim function
"""


def get_serialization_paths(platform, serialization_exp_id):
    exp = Experiment.from_id(serialization_exp_id, children=False)
    exp.simulations = platform.get_children(exp.id, exp.item_type,
                                            children=["tags", "configuration", "files", "hpc_jobs"])

    sim_dict = {'Larval_Capacity': [], 'Outpath': []}
    for simulation in exp.simulations:
        # if simulation.tags['Run_Number'] == 0:
        string = simulation.get_platform_object().hpc_jobs[0].working_directory.replace('internal.idm.ctr', 'mnt')
        string = string.replace('\\', '/')
        string = string.replace('IDM2', 'idm2')

        sim_dict['Larval_Capacity'] += [float(simulation.tags['Larval_Capacity'])]
        sim_dict['Outpath'] += [string]

    df = pd.DataFrame(sim_dict)
    return df


def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # config = set_config.set_config( config )

    import emodpy_malaria.malaria_config as conf
    config = conf.set_team_defaults(config, manifest)
    conf.add_species(config, manifest, ["gambiae", "funestus", "arabiensis"])
    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialization_Mask_Node_Read = 0
    config.parameters.Serialized_Population_Path = manifest.assets_input_dir # <--we uploaded files to here
    config.parameters.Serialized_Population_Filenames = ["state-00020-000.dtk", "state-00020-001.dtk"]

    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp

    import emodpy_malaria.interventions.bednet as bednet

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file

    # print( f"Telling emod-api to use {manifest.schema_file} as schema." ) 
    camp.add(bednet.Bednet(camp.schema_path, start_day=100, coverage=1.0, killing_eff=1.0, blocking_eff=1.0, usage_eff=1.0,
                           node_ids=[]))
    return camp


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demog = Demographics.from_params(tot_pop=100, num_nodes=4)
    return demog


def general_sim(erad_path, serialized_exp_id):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", num_cores=2, node_group="idm_48cores", priority="Highest")
    experiment_name = "Create simulation from serialized files"


    task = EMODTask.from_default2(
        config_path="my_config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_custom_cb=None,
        demog_builder=build_demog,
        plugin_report=None  # report
    )

    # Create simulation sweep with builder
    builder = SimulationBuilder()

    serialized_population_path_df = get_serialization_paths(platform=platform, serialization_exp_id=serialized_exp_id)

    func = partial(update_serialize, serialization=serialization, sim_duration=10 * 365,
                   serialized_population_path_df=serialized_population_path_df)
    builder.add_sweep_definition(func, [7.0, 7.25, 7.5, 7.75, 8.0])

    builder.add_sweep_definition(update_sim_random_seed, range(params.nSims))
    func = partial(update_camp_type, serialize=serialization, sim_duration=10 * 365)
    builder.add_sweep_definition(func, [True, False])
    exp_name = params.exp_name

    # Add reporter
    add_report_vector_genetics(task, manifest, species="gambiae")


    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

    print("Adding asset dir...")
    task.common_assets.add_directory(assets_directory=manifest.serialization_files)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.uid.hex)
    print()
    print(experiment.uid.hex)



if __name__ == "__main__":
    serialization = 0
    serialized_exp_id = 0
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim(serialization, serialized_exp_id)
