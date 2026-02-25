#!/usr/bin/env python3
import argparse
import os
import pathlib  # for a join
import sys
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy_malaria.reporters.builtin import ReportVectorGenetics, ReportVectorStats
import emod_api.config.default_from_schema_no_validation as dfs

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

"""
    We create a simulation with SpaceSpraying campaign and
    sweep over several parameters of the campaign.

"""


# When you're doing a sweep across campaign parameters, you want those parameters exposed
# in the build_campaign function as done here
def build_campaign(bednet_start_day=1, bednet_coverage=1,
                   spraying_coverage=1.0,
                   ivermectin_killing_initial=1):
    """
        Creates and returns the full campaign file.
        Campaign file contains all the interventions that will be distributed (ran) over the course of the simulation.
        The file is created on the server and can be modified using the partial and callback functions below for each
        simulation. The exposed parameters are the ones that can be modified at the time of
        campaign file creating
    Args:
        bednet_start_day: start_day parameter value for the bednet intervention
        bednet_coverage: demographic_overage parameter value for the bednet intervention
        spraying_coverage: spray_coverage parameter value for the space spraying
        ivermectin_killing_initial: killing_initial_effect parameter value for the ivermectin

    Returns:
        Configured campaign

    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.spacespraying as spray
    import emodpy_malaria.interventions.ivermectin as ivermectin
    from emodpy_malaria.interventions.usage_dependent_bednet import add_scheduled_usage_dependent_bednet
    # passing in manifest
    campaign.set_schema(manifest.schema_file)
    add_scheduled_usage_dependent_bednet(campaign, start_day=bednet_start_day, demographic_coverage=bednet_coverage)
    spray.add_scheduled_space_spraying(campaign, start_day=15, spray_coverage=spraying_coverage,
                                       killing_initial_effect=0.85,
                                       killing_box_duration=50,
                                       killing_decay_time_constant=33)

    ivermectin.add_scheduled_ivermectin(campaign=campaign,
                                        start_day=20,
                                        demographic_coverage=0.57,
                                        killing_initial_effect=ivermectin_killing_initial,
                                        killing_box_duration=2,
                                        killing_decay_time_constant=0.25)
    return campaign


def update_campaign_multiple_parameters(simulation, bednet_start_day, bednet_coverage,
                                        spraying_coverage,
                                        ivermectin_killing_initial):
    """
        This is a callback function that updates several parameters in the build_campaign function.
        the sweep is achieved by the itertools creating a an array of inputs with all the possible combinations
        see builder.add_sweep_definition(update_campaign_multiple_parameters function below
    Args:
        simulation: simulation object to which we will attach the callback function
        bednet_start_day: start_day parameter value for the bednet intervention
        bednet_coverage: demographic_overage parameter value for the bednet intervention
        spraying_coverage: spray_coverage parameter value for the space spraying
        ivermectin_killing_initial: killing_initial_effect parameter value for the ivermectin

    Returns:
        a dictionary of tags for the simulation to use in COMPS
    """

    build_campaign_partial = partial(build_campaign, bednet_start_day=bednet_start_day, bednet_coverage=bednet_coverage,
                                     spraying_coverage=spraying_coverage,
                                     ivermectin_killing_initial=ivermectin_killing_initial)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return dict(bednet_start_day=bednet_start_day, bednet_coverage=bednet_coverage,
                spraying_coverage=spraying_coverage, ivermectin_killing_initial=ivermectin_killing_initial)


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    config.parameters.Simulation_Duration = 80

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=10000, name=1, forced_id=1)
    return demographics


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=None,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demographics
    )

    # Set platform
    platform = Platform("Container", job_directory="../example_jobs")

    # Create simulation sweep with builder
    # sweeping over start day AND killing effectiveness - this will be a cross product
    builder = SimulationBuilder()

    # this will sweep over the entire parameter space in a cross-product fashion
    # you will get 2x3x3x2=36 simulations
    builder.add_multiple_parameter_sweep_definition(
        update_campaign_multiple_parameters,
        dict(
            bednet_start_day=[3, 5],
            bednet_coverage=[0.95, 0.87, 0.58],
            spraying_coverage=[0.95, 0.87, 0.58],
            ivermectin_killing_initial=[0.79, 0.51]
        )
    )

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name="campaign_sweep")

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    print()
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
    else:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as fd:
            fd.write(experiment.id)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
