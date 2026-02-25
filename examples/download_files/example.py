#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask

import manifest


def update_sim_bic(simulation, value):
    simulation.task.config.parameters.Base_Infectivity_Constant = value * 0.1
    return {"Base_Infectivity": value}


def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["funestus"])

    config.parameters.Simulation_Duration = 80

    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emodpy_malaria.interventions.ivermectin as ivermectin

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file

    ivermectin.add_scheduled_ivermectin(
        campaign=camp,
        killing_initial_effect=0.78, demographic_coverage=0.63,
        target_num_individuals=None, killing_box_duration=20,
        killing_decay_time_constant=14
    )

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
    import emodpy_malaria.demographics.MalariaDemographics as Demographics

    demog = Demographics.from_params(tot_pop=2e4, num_nodes=1, frac_rural=0.5,
                                     id_ref="cwiswell_single_node_malaria")

    return demog


def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")

    # create EMODTask 
    print("Creating EMODTask (from files)...")

    task = EMODTask.from_default2(
        config_path="my_config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        param_custom_cb=set_config_parameters,
        ep4_custom_cb=None,
        demog_builder=build_demog,
        plugin_report=None  # report
    )

    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)

    # print("Adding asset dir...")
    # task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)
    print("Adding local assets (py scripts mainly)...")

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_sim_random_seed, range(10))

    # create experiment from builder
    print(f"Prompting for COMPS creds if necessary...")
    experiment = Experiment.from_builder(builder, task, name="Ivermectin sample experiment")
    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
        exit()

    print(f"Experiment {experiment.id} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.id)

    # THIS IS WHERE WE DOWNLOAD THE FILE

    from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType

    # navigating to the experiment_id file to retrieve experiment id
    dl_wi = DownloadWorkItem(
        related_experiments=[experiment.id],
        file_patterns=["output/*.json"],
        simulation_prefix_format_str='serialization_files',
        verbose=True,
        output_path="",
        delete_after_download=False,
        include_assets=True,
        compress_type=CompressType.deflate)

    dl_wi.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
        exit()

    print(f"Experiment {experiment.id} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.id)
    print()
    print(experiment.id)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
