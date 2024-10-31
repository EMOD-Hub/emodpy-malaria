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


import manifest

# ****************************************************************
# This is an example template with the most basic functions
# which create config and demographics from pre-set defaults
# and adds one intervention to campaign file. Runs the simulation
# and writes experiment id into experiment_id
#
# ****************************************************************


def build_campaign():
    """
        Creating empty campaign. For adding interventions please find intervention name in the examples
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign

    return campaign


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "funestus", "minimus"])
    config.parameters.Simulation_Duration = 80

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.


    """
    # extends emod_api.demographics.Demographics
    # this has ability to set various attributes, properties, distributions, access nodes
    import emodpy_malaria.demographics.MalariaDemographics as demog

    # please go to the file to look up what distributions are pre-defined
    import emod_api.demographics.PreDefinedDistributions as Distributions

    # create basic demographics object from a csv that has node ids, lat, long for the node.
    # your csv file can have headers for node ids, latitutude, longtitude, population, and birth rate
    demog = demog.from_csv("Ratanikiri.csv", id_ref="Gridded world grump30arcsec")

    # get a pre-definied age distribution for Distributions
    age_distribution = Distributions.AgeDistribution_Mosambique
    # set it using the demographics object
    demog.SetAgeDistribution(age_distribution)

    # Set MortalityDistribution in one step
    demog.SetMortalityDistribution(Distributions.SEAsia_Diag)

    # Set Initial Prevalence with uniform distribution
    demog.SetInitPrevFromUniformDraw(0.13, 0.15)
    # Set constant risk
    demog.SetConstantRisk(1)


    # Add IndividualProperties
    initial_distribution = [0.7, 0.3]
    demog.AddIndividualPropertyAndHINT(Property="ForestGoing", Values=["HatesForest", "LovesForest"],
                                       InitialDistribution=initial_distribution)
    demog.AddIndividualPropertyAndHINT(Property="HomeVillage", Values=["Village1", "Village2", "Forest"],
                                       InitialDistribution=[1, 0, 0])

    # get node by node id, returns emod_api.demographics.Node object
    # and edit that node's birth rate
    demog.get_node(1).birth_rate = 0.02


    # set larval_habitat_multiplier for each node
    schema_path = manifest.schema_file
    demog.add_larval_habitat_multiplier(schema_path, "CONSTANT", 0.31, species="ALL_SPECIES", node_id=1)
    demog.add_larval_habitat_multiplier(schema_path, "LINEAR_SPLINE", 0, species="ALL_SPECIES", node_id=1)
    demog.add_larval_habitat_multiplier(schema_path, "WATER_VEGETATION", 0, species="gambiae", node_id=1)
    demog.add_larval_habitat_multiplier(schema_path, "WATER_VEGETATION", 0.31, species="minimus", node_id=1)

    return demog


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores")

    experiment_name = "create_demographics_example"

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
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

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


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
