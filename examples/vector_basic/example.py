#!/usr/bin/env python3

# idmtools ...

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask

from emodpy_malaria import vector_config as vector_config
import manifest

"""
In this example, we add vector genetics to the vector population and insecticide resistance, 
adds a VectorGeneticsReporter.
The important bits are in set_param_fn, build_campaign.
"""

def set_param_fn(config):
    """
        Sets configuration parameters from the malaria defaults and explicitly sets
        the vector genetics paramters and insecticide resistance parameters
    Args:
        config:

    Returns:
        completed config
    """
    vector_config.set_team_defaults(config, manifest)  # team defaults
    vector_config.add_species(config, manifest, species_to_select=["gambiae"])

    config.parameters.Incubation_Period_Constant = 0
    config.parameters.Infectious_Period_Constant = 100

    config.parameters.Simulation_Duration = 365

    return config


def build_campaign():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.bednet as bednet
    import emodpy_malaria.interventions.mosquitorelease as mr

    campaign.set_schema(manifest.schema_file)

    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )
    bednet.add_itn_scheduled(campaign,
                             start_day=200,
                             demographic_coverage=.5,
                             killing_initial_effect=0.7,
                             blocking_initial_effect=0.5,
                             usage_initial_effect=0.5)

    # mr.add_scheduled_mosquito_release(campaign, start_day=1, released_number=20000, released_infectious=0.2,
    #                                   released_species="gambiae",
    #                                   released_genome=[["X", "X"], ["a", "b"], ["three", "three"]])

    return campaign


def build_demog():
    """
        Builds demographics
    Returns:
        complete demographics
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    demog = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1, init_prev=0.1)

    return demog


def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    experiment_name = "Vector Hello World example"

    # create EMODTask 
    print("Creating EMODTask (from files)...")
    task = EMODTask.from_default2(
        config_path="my_config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_custom_cb=None,
        demog_builder=build_demog,
        plugin_report=None  # report
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
    print()
    print(experiment.id)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
