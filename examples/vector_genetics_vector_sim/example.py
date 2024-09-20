#!/usr/bin/env python3

# idmtools ...

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy_malaria.reporters.builtin import *

from emodpy_malaria import vector_config as vector_config
import manifest

"""
In this example, we add vector genetics to the vector population, 
adds a VectorGeneticsReporter.
The important bits are in set_param_fn, and build_campaign()
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
    config.parameters.Simulation_Type = "VECTOR_SIM"
    vector_config.set_team_defaults(config, manifest)  # team defaults
    vector_config.add_species(config, manifest, ["gambiae"])

    # add gender alleles; they need to be first, per #4576
    vector_config.add_genes_and_alleles(config, manifest, "gambiae",
                                        [("X1", 0.25), ("X2", 0.25), ("Y1", 0.15, 1), ("Y2", 0.35, 1)])

    # Vector Genetics, the main purpose of this example.
    vector_config.add_genes_and_alleles(config, manifest, "gambiae", [("a", 0.5), ("b", 0.5), ("c", 0)])
    vector_config.add_mutation(config, manifest, "gambiae", mutate_from="a", mutate_to="b", probability=0.05)
    vector_config.add_mutation(config, manifest, "gambiae", mutate_from="b", mutate_to="c", probability=0.1)
    vector_config.add_mutation(config, manifest, "gambiae", mutate_from="c", mutate_to="a", probability=0.1)
    vector_config.add_mutation(config, manifest, "gambiae", mutate_from="a", mutate_to="c", probability=0.03)

    # another set of alleles
    vector_config.add_genes_and_alleles(config, manifest, "gambiae", [("one", 0.9), ("two", 0.05), ("three", 0.05)])
    vector_config.add_mutation(config, manifest, "gambiae", mutate_from="one", mutate_to="three", probability=0.04)

    # these are the traits/benefits based on the alleles
    # protects vectors from infection
    vector_config.add_trait(config, manifest, "gambiae", [["X1", "X1"]], [("INFECTED_BY_HUMAN", 0)])
    # vectors make more eggs
    vector_config.add_trait(config, manifest, "gambiae", [["b", "b"], ["one", "two"]], [("FECUNDITY", 10),
                                                                                        ("INFECTED_BY_HUMAN", 0.37)])
    vector_config.add_species_drivers(config, manifest, species="gambiae", driver_type="X_SHRED", driving_allele="one",
                                      to_copy="one",
                                      to_replace="two", likelihood_list=[("one", 0.9), ("two", 0.1)],
                                      shredding_allele_required="Y2", allele_to_shred="X2", allele_to_shred_to="X1",
                                      allele_shredding_fraction=0.7, allele_to_shred_to_surviving_fraction=0.03)

    config.parameters.Simulation_Duration = 10

    return config


def build_campaign():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.mosquitorelease as mr

    # This isn't desirable. Need to think about right way to provide schema (once)
    campaign.set_schema(manifest.schema_file)

    mr.add_scheduled_mosquito_release(campaign, start_day=1, released_number=20000, released_infectious=0.2,
                                      released_species="gambiae",
                                      released_genome=[["X1", "X1"], ["one", "two"], ["b", "b"]])

    return campaign


def build_demog():
    """
        Builds demographics
    Returns:
        complete demographics
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    demog = Demographics.from_params(tot_pop=20, num_nodes=1)
    demog.SetBirthRate(0)

    return demog


def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    # Set platform
    # platform = Platform("SLURMStage") # to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    experiment_name = "Vector Genetics VECTOR_SIM example"

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

    add_report_vector_genetics(task, manifest, species="gambiae", include_vector_state=False,
                               allele_combinations_for_stratification=[["a"], ["b"]])

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
    with open(manifest.experiment_id, "w") as fd:
        fd.write(experiment.uid.hex)
    print()
    print(experiment.uid.hex)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
