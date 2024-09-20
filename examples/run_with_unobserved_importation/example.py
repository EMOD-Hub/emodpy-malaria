#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

import numpy as np

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
import emodpy_malaria.malaria_config as malaria_config
from emodpy_malaria.reporters.builtin import *
import itertools

import manifest

# ****************************************************************
# This is an example template with the most basic functions
# which create config and demographics from pre-set defaults
# and adds one intervention to campaign file. Runs the simulation
# and writes experiment id into experiment_id
#
# ****************************************************************


seasonality = {
    'seasonal_high': [
        3,
        0.8,
        1.25,
        0.1,
        2.7,
        10,
        6,
        35,
        2.8,
        1.5,
        1.6,
        2.1
    ],
    'seasonal_low': [
        1,
        0.8,
        1.25,
        0.6,
        1.9,
        4,
        3,
        6,
        2,
        1,
        0.8,
        0.9],
    'seasonal_verylow': [
        1,
        0.9,
        1.05,
        0.85,
        1.2,
        1.5,
        2,
        2,
        1.3,
        1,
        0.95,
        0.9],

    'constant': [1] * 12}


def build_campaign(scale_factor=1):
    """
        Creating empty campaign. For adding interventions please find intervention name in the examples
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.outbreak as outbreak

    campaign.set_schema(manifest.schema_file)
    outbreak.add_outbreak_individual(campaign,
                                     demographic_coverage=0.001 * scale_factor,
                                     repetitions=-1,
                                     timesteps_between_repetitions=1)

    return campaign


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    """
    Using config generated from schema and overlaying settings manually directly from the
    example config.json file
    """

    import json

    # the parameters in list have changed formats, so we're not copying them over directly
    ignore_list = ["Vector_Species_Params", "Malaria_Drug_Params"]
    with open('config_jon.json') as f:
        jon_config = json.load(f)
        for parameter in jon_config["parameters"]:
            if parameter not in ignore_list:
                config["parameters"][parameter] = jon_config["parameters"][parameter]

    # setting team drug params
    config = malaria_config.set_team_drug_params(config, manifest)

    years = 0.1  # length of simulation, in years
    config.parameters.Simulation_Duration = years * 365
    config.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION"
    # manually inserting as it was the easiest to just copy the vector params and update larval_habitat_types
    # instead of creating everything and assigning stuff
    malaria_config.add_species(config, manifest, species_to_select=["gambiae"])
    malaria_config.set_species_param(config, "gambiae", "Acquire_Modifier", 0.8)
    malaria_config.set_species_param(config, "gambiae", "Indoor_Feeding_Fraction", 0.5)
    malaria_config.set_species_param(config, "gambiae", "Vector_Sugar_Feeding_Frequency", "VECTOR_SUGAR_FEEDING_EVERY_DAY")

    # configuring the habitat using schema parameters so we can add it as one "parameter"
    import emod_api.config.default_from_schema_no_validation as dfs
    lht = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
    lht.parameters.Habitat_Type = "LINEAR_SPLINE"
    lht.parameters.Max_Larval_Capacity = 159242868.22139877
    lht.parameters.Capacity_Distribution_Number_Of_Years = 1
    # adding larval capacity
    cdot = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:InterpolatedValueMap"])
    cdot.parameters.Times = [0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167,
                             334.583]
    cdot.parameters.Values = [1, 0.9, 1.05, 0.85, 1.2, 1.5, 2, 2, 1.3, 1, 0.95, 0.9]
    lht.parameters.Capacity_Distribution_Over_Time = cdot.parameters
    # set our configured habitat for gambiae
    malaria_config.set_species_param(config, "gambiae", "Habitats", [lht.parameters])
    return config


def scale_linear_spline_max_habitat_and_pop(simulation, values):
    # when habitat scalar is proportional to the population scalar and we
    # want them to be swept together
    pop_multiplier = values[0]
    habitat_scale_factor = values[1] * values[0]
    seasonality_profile = values[2]
    for species_params in simulation.task.config.parameters.Vector_Species_Params:
        habitats = species_params["Habitats"]
        for habitat in habitats:
            if habitat["Habitat_Type"] == "LINEAR_SPLINE":
                habitat["Max_Larval_Capacity"] = habitat["Max_Larval_Capacity"] * habitat_scale_factor
                habitat["Capacity_Distribution_Over_Time"]["Values"] = seasonality[seasonality_profile]
    simulation.task.config.parameters.x_Base_Population = pop_multiplier
    return {'pop_scalar': pop_multiplier, 'habitat_multiplier': habitat_scale_factor,
            "seasonality_profile": seasonality_profile}


def scale_local_migration(simulation, scale_factor):
    simulation.task.config.parameters.x_Local_Migration = scale_factor
    return {'migration_scalar': scale_factor}


def scale_importation(simulation, scale_factor):
    build_campaign_partial = partial(build_campaign, scale_factor=scale_factor)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {'outbreak_scalar': scale_factor}


def update_run_number(simulation, run_number):
    simulation.task.config.parameters.Run_Number = run_number
    return {'run_number': run_number}


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.

    """
    # import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    import emod_api.demographics.Demographics as Demographics

    demographics = Demographics.from_file(f"inputs//Namawala_single_node_demographics_balanced_pop_growth.json")

    return demographics


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    #platform = Platform("SLURMStage")  # to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores")

    num_seeds = 5
    report_start = 20
    pop_multipliers = [0.1, 0.2, 0.5, 1, 2]
    import_scalar = [0, 2, 5, 10]
    habitat_multipliers = [0.2]
    seasonality_profile = 'seasonal_high'
    experiment_name = f'genepi_test_suite_sweep_popsize_importation_season_{seasonality_profile}'

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demographics
    )

    # adding reporter
    add_malaria_transmission_report(task, manifest, start_day=report_start)

    # setting up all the sweeping
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_run_number, range(num_seeds))
    builder.add_sweep_definition(scale_importation, import_scalar)

    # because the habitat multiplier is dependent on pop_multiplier, I put them into the same function,
    # otherwise they would be swept over independently and we don't want that
    builder.add_sweep_definition(scale_linear_spline_max_habitat_and_pop,
                                 list(itertools.product(pop_multipliers, habitat_multipliers, [seasonality_profile])))

    experiment = Experiment.from_builder(builder, task, experiment_name)
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


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
