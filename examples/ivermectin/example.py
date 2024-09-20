#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
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
       Adding a scheduled ivermectin intervention
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.ivermectin import add_scheduled_ivermectin, add_triggered_ivermectin

    # passing in schema file to verify that everything is correct.
    campaign.set_schema(manifest.schema_file)

    add_scheduled_ivermectin(campaign=campaign,
                             start_day=20,
                             target_num_individuals=43,
                             demographic_coverage=0.95,  # will be ignored because we have target_num_individuals set
                             killing_initial_effect=0.65,
                             killing_box_duration=2,
                             killing_decay_time_constant=25,
                             cost=22,
                             insecticide="Example",
                             intervention_name="Ivermectin1")
    add_scheduled_ivermectin(campaign=campaign,
                             start_day=2,
                             demographic_coverage=0.95,  # will be ignored because we have target_num_individuals set
                             killing_initial_effect=0.77,
                             killing_box_duration=0,
                             killing_decay_time_constant=50,
                             insecticide="Example",
                             intervention_name="Ivermectin2")

    add_triggered_ivermectin(campaign=campaign,
                             start_day=20,
                             demographic_coverage=0.57,
                             trigger_condition_list=["HappyBirthday", "Births"],
                             delay_period_constant=7,
                             listening_duration=33,
                             # ind_property_restrictions=["Risk:High"],
                             killing_initial_effect=0.88,
                             killing_box_duration=0,
                             killing_decay_time_constant=0,
                             insecticide="Example",
                             intervention_name="Ivermectin3"
                             )
    add_triggered_ivermectin(campaign=campaign,
                             start_day=20,
                             trigger_condition_list=["HappyBirthday", "Births"],
                             killing_initial_effect=0.88,
                             killing_box_duration=66,
                             killing_decay_time_constant=0,
                             insecticide="Example",
                             intervention_name="Ivermectin3"
                             )
    return campaign


def set_config_parameters(config):
    """
        This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    Args:
        config:

    Returns:
        configuration settings
    """

    # You have to set simulation type explicitly before you set other parameters for the simulation
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])
    vector_config.add_genes_and_alleles(config, manifest, "gambiae", [("a", 0.5), ("b", 0.5), ("c", 0)])
    malaria_config.add_insecticide_resistance(config, manifest, insecticide_name="Example",
                                              allele_combo=[["a", "a"]],
                                              species="gambiae", blocking=0.2, killing=0.3, repelling=0)

    return config


def build_demographics():
    """
        Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.
    Returns:
        demographics.. object???
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1)
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

    experiment_name = "Ivermectin_Example"

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

    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

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
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
