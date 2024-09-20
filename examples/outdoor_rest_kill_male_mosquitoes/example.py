#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy_malaria.reporters.builtin import *
import emod_api.config.default_from_schema_no_validation as dfs

from emodpy_malaria import malaria_config as malconf
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


def update_camp_start_day(simulation, value):
    # simulation.task.config.parameters.Run_Number = value
    build_camp_partial = partial(build_camp, actual_start_day=80 + value * 10)
    simulation.task.create_campaign_from_callback(build_camp_partial)
    return {"Start_Day": 80 + value * 10}


def update_killing_config_effectiveness(simulation, value):
    # simulation.task.config.parameters.Run_Number = value
    build_camp_partial = partial(build_camp, current_insecticide="only_kill_male_funestus",
                                 killing_effectiveness=value)
    simulation.task.create_campaign_from_callback(build_camp_partial)
    return {"killing_effectiveness": value}


def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config = malconf.set_team_defaults(config, manifest)
    malconf.add_species(config, manifest, ["gambiae", "funestus", "arabiensis"])
    config.parameters.Egg_Saturation_At_Oviposition = "SATURATION_AT_OVIPOSITION"
    config.parameters.Enable_Vector_Species_Report = 1
    config.parameters.Simulation_Duration = 90

    # add sugar feeding
    malconf.set_species_param(config, "gambiae", "Vector_Sugar_Feeding_Frequency",
                              "VECTOR_SUGAR_FEEDING_EVERY_FEED")

    malconf.set_species_param(config, "funestus", "Vector_Sugar_Feeding_Frequency",
                              "VECTOR_SUGAR_FEEDING_EVERY_FEED")

    malconf.set_species_param(config, "arabiensis", "Vector_Sugar_Feeding_Frequency",
                              "VECTOR_SUGAR_FEEDING_EVERY_FEED")

    # add insecticide resistance
    malconf.add_insecticide_resistance(config, manifest,
                                       insecticide_name="only_kill_male_funestus",
                                       species="gambiae",
                                       allele_combo=[["X", "*"]],
                                       killing=0.0)  # Makes gambiae unaffected
    malconf.add_insecticide_resistance(config, manifest,
                                       insecticide_name="only_kill_male_funestus",
                                       species="funestus",
                                       allele_combo=[["X", "X"]],
                                       killing=0.0)  # Makes female funestus unaffected

    return config


def build_camp(actual_start_day=90, current_insecticide="only_kill_male_funestus",
               killing_effectiveness=0.5):
    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.outdoorrestkill import add_outdoorrestkill
    campaign.set_schema(manifest.schema_file)
    add_outdoorrestkill(campaign, start_day=actual_start_day,
                        insecticide=current_insecticide,
                        killing_initial_effect=killing_effectiveness,
                        killing_box_duration=10, killing_decay_time_constant=1 / 0.07)

    return campaign


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demog = Demographics.from_template_node(lat=0, lon=0, pop=10000, name=1, forced_id=1)
    return demog


def ep4_fn(task):
    task = emod_task.add_ep4_from_path(task, manifest.ep4_path)
    return task


def general_sim(erad_path, ep4_scripts):
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    platform = Platform("Calculon", num_cores=1, node_group="idm_48cores", priority="Highest")
    # create EMODTask 
    print("Creating EMODTask (from files)...")

    task = emod_task.EMODTask.from_default2(
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
    
    # print("Adding asset dir...")
    # task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)
    add_report_vector_stats(task, manifest, species_list=["gambiae", "funestus", "arabiensis"])

    # Set task.campaign to None to not send any campaign to comps since we are going to override it later with
    # dtk-pre-process.
    print("Adding local assets (py scripts mainly)...")

    seeds = 1
    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_sim_random_seed, range(seeds))
    builder.add_sweep_definition(update_killing_config_effectiveness, [0.0, 0.2, 0.4, 0.8, 1.0])

    # create experiment from builder
    print(f"Prompting for COMPS creds if necessary...")
    experiment = Experiment.from_builder(builder, task,
                                         name="Malaria OutdoorRestKill Male Vectors")

    # other_assets = AssetCollection.from_id(pl.run())
    # experiment.assets.add_assets(other_assets)

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


def run_test(erad_path):
    general_sim(erad_path, ["dtk_post_process.py"])


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_test(manifest.eradication_path)
