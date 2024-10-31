#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
# from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection
# from idmtools_models.templated_script_task import get_script_wrapper_unix_task

# emodpy
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
import emod_api.config.default_from_schema_no_validation as dfs
from emodpy_malaria.reporters.builtin import *

import params
import manifest


# ****************************************************************
# Features to support:
#
#  Read experiment info from a json file
#  Add Eradication.exe as an asset (Experiment level)
#  Add Custom file as an asset (Simulation level)
#  Add the local asset directory to the task
#  Use builder to sweep simulations
#  How to run dtk_pre_process.py as pre-process
#  Save experiment info to file
# ****************************************************************

def update_sim_bic(simulation, value):
    simulation.task.config.parameters.Base_Infectivity_Constant = value * 0.1
    return {"Base_Infectivity": value}


def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def print_params():
    """
    Just a useful convenience function for the user.
    """
    # Display exp_name and nSims
    # TBD: Just loop through them
    print("exp_name: ", params.exp_name)
    print("nSims: ", params.nSims)


def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """

    import emodpy_malaria.malaria_config as conf
    config.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION"
    config.parameters.Enable_Vector_Species_Report = 1
    config.parameters.Enable_Migration_Heterogeneity = 0
    config = conf.set_team_defaults(config, manifest)
    conf.add_species(config, manifest, ["gambiae"])
    config.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emodpy_malaria.interventions.bednet as bednet
    from emodpy_malaria.interventions.irs import add_scheduled_irs_housing_modification
    from emodpy_malaria.interventions.drug import add_scheduled_antimalarial_drug
    from emodpy_malaria.interventions.outbreak import add_outbreak_individual

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file

    add_outbreak_individual(campaign=camp, start_day=1, demographic_coverage=0.3)
    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )
    add_scheduled_irs_housing_modification(campaign=camp, start_day=100, demographic_coverage=0.5,
                                           repelling_initial_effect=0.5, killing_initial_effect=0.5)

    add_scheduled_antimalarial_drug(campaign=camp, start_day=20, demographic_coverage=0.3,
                                    drug_type="Artemether")
    """
    add_IRS(cb, start=start,
            coverage_by_ages=[{'coverage': coverage}],
            killing_config=WaningEffectBoxExponential(
                Initial_Effect=0.5,
                Decay_Time_Constant=150,
                Box_Duration=90
            ),
            nodeIDs=nodes)
    add_drug_campaign(cb, campaign_type= 'MDA', drug_code=drug, start_days=start_days, repetitions=1, tsteps_btwn_repetitions=30,
                      coverage=coverage, target_group={'agemin': 0, 'agemax': agemax})
    """
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
    import emod_api.migration as mig

    demog = Demographics.from_params(tot_pop=2e4, num_nodes=2, frac_rural=0.5, id_ref="jonr_dual_node_malaria")
    mig = mig.from_params(pop=2e4, num_nodes=2, frac_rural=0.5, id_ref="jonr_dual_node_malaria",
                          migration_type=mig.Migration.REGIONAL)

    return demog, mig


def add_reports(task, manifest):
    """
    Inbox:
    """

    add_malaria_summary_report(task, manifest, filename_suffix="Annual Report",
                               start_day=2 * 365, reporting_interval=365, max_number_reports=1,
                               age_bins=[2, 10, 125], parasitemia_bins=[0, 50, 200, 500, 2000000])
    add_human_migration_tracking(task, manifest)

    add_malaria_cotransmission_report(task, manifest, start_day=1, end_day=1 + 1 * 365,
                                      filename_suffix="Jon's Transmission Report")


def general_sim(erad_path, ep4_scripts):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    print_params()

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")

    # pl = RequirementsToAssetCollection( platform, requirements_path=manifest.requirements )

    # create EMODTask 
    print("Creating EMODTask (from files)...")

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

    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)

    add_reports(task, manifest)

    # print("Adding asset dir...")
    # task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)
    print("Adding local assets (py scripts mainly)...")

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_sim_random_seed, range(params.nSims))

    # create experiment from builder
    print(f"Prompting for COMPS creds if necessary...")
    experiment = Experiment.from_builder(builder, task, name=params.exp_name)

    # other_assets = AssetCollection.from_id(pl.run())
    # experiment.assets.add_assets(other_assets)

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
    print()
    print(experiment.id)


def run_test(erad_path):
    general_sim(erad_path, manifest.my_ep4_assets)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_test(manifest.eradication_path)
