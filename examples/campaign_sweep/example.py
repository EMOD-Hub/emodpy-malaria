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
def build_campaign(start_day=1, coverage=1.0, killing_effect=0, constant_duration=25):
    """
        Adds a SpaceSpraying intervention, using parameters passed in.
    Args:
        start_day: the day the intervention goes in effect
        coverage: portion of each node covered by the intervention
        killing_effect: portion of vectors killed by the intervention
        constant_duration: the duration of effectiveness of the SpaceSpraying
    Returns:
        completed campaign
    """
    # adds a SpaceSpraying intervention
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.spacespraying as spray
    import emodpy_malaria.interventions.ivermectin as ivermectin
    from emodpy_malaria.interventions.usage_dependent_bednet import add_scheduled_usage_dependent_bednet
    # passing in manifest
    campaign.set_schema(manifest.schema_file)
    add_scheduled_usage_dependent_bednet(campaign, start_day=start_day, demographic_coverage=coverage)
    spray.add_scheduled_space_spraying(campaign, start_day=start_day, spray_coverage=coverage,
                                       killing_initial_effect=killing_effect, killing_box_duration=constant_duration,
                                       killing_decay_time_constant=33)

    ivermectin.add_scheduled_ivermectin(campaign=campaign,
                                        start_day=20,
                                        demographic_coverage=0.57,
                                        killing_initial_effect=0.65,
                                        killing_box_duration=2,
                                        killing_decay_time_constant=0.25)
    return campaign


def update_campaign_start_day(simulation, value):
    """
        This callback function updates the start day of the campaign.
        to use: Please un-comment builder.add_sweep_definition(update_campaign_start_day, etc)
    Args:
        simulation:
        value: value to which the start_day will be set

    Returns:
        tag that will be added to the simulation run
    """
    build_campaign_partial = partial(build_campaign, star_day=value)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"start_day": value}


def update_campaign_multiple_parameters(simulation, values):
    """
        This is a callback function that updates several parameters in the build_campaign function.
        the sweep is achieved by the itertools creating a an array of inputs with all the possible combinations
        see builder.add_sweep_definition(update_campaign_multiple_parameters function below
    Args:
        simulation: simulation object to which we will attach the callback function
        values: a list of values to assign to this particular simuation

    Returns:
        tags for the simulation to use in comps
    """
    build_campaign_partial = partial(build_campaign, start_day=values[0], coverage=values[1],
                                     killing_effect=values[2])
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"start_day": values[0], "spray_coverage": values[1], "killing_effectiveness": values[2]}


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

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")

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
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # Create simulation sweep with builder
    # sweeping over start day AND killing effectiveness - this will be a cross product
    builder = SimulationBuilder()

    # this sweeps over one parameter, calling several of these one-parameter sweeps in
    # this script will cause only the last parameter to be swept, but there will be a cross-product-of-the-sweeps
    # number of simulations created.
    # comment out the builder below when using this
    # builder.add_sweep_definition(update_campaign_start_day, [23, 3, 84, 1])

    # this is how you sweep over a multiple-parameters space:
    # itertools product creates a an array with all the combinations of parameters (cross-product)
    # so, 2x3x2 = 12 simulations
    import itertools
    # .product([start_days],[spray_coverages], [killing_effectivenesses])
    builder.add_sweep_definition(update_campaign_multiple_parameters,
                                 list(itertools.product([3, 5], [0.95, 0.87, 0.58], [0.79, 0.51])))

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name="Campaign Sweep, SpaceSpraying")

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
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
