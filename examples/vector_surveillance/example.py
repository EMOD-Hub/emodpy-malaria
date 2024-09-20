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
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy_malaria.reporters.builtin import *
from emodpy_malaria.interventions.vector_surveillance import *

from emodpy_malaria import vector_config as vector_config
import manifest

"""
In this example, we add vector genetics to the vector population and insecticide resistance, 
adds a VectorGeneticsReporter.
The important bits are in set_param_fn, build_campaign.
"""

# declaring the variable for events that will be used in the campaigns and reporters, so they are consistent
# and can be easily changed if needed and available to all the functions
start_surveillance = "start_surveillance"
completion_event_a1 = "DoneReleasing_a1a1"
completion_event_b1 = "DoneReleasing_b1b1"
release_a1 = "Release_More_Mosquitoes_a1a1"
release_a1b1 = "Release_More_Mosquitoes_a1b1"
completion_event_ind = "DoneReleasing_ind_events"
release_ind_events = "Release_ind_Events"
genome_counter_ran = "Genome_Counter_Ran"
frequency_counter_ran = "Frequency_Counter_Ran"
stop_surveillance = "stop_surveillance"

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

    # the following lines define alleles, mutations and traits and they need "set_genetics" to actually be added
    # Vector Genetics, the main purpose of this example.
    vector_config.add_genes_and_alleles(config, manifest, "gambiae", [("a0", 0.9), ("a1", 0.1)])
    vector_config.add_genes_and_alleles(config, manifest, "gambiae", [("b0", 0.9), ("b1", 0.1)])

    config.parameters.Simulation_Duration = 300

    return config


def build_campaign():
    """
    Build the logic of when, where, and to whom interventions are distributed
    """
    import emod_api.campaign as campaign
    from emod_api.interventions.common import add_broadcast_coordinator_event, add_triggered_coordinator_event
    from emodpy_malaria.interventions.mosquitorelease import _mosquito_release
    from emodpy_malaria.interventions.ivermectin import _ivermectin
    from emodpy_malaria.interventions.bednet import _simple_bednet
    from emod_api.utils import Distributions

    # always use set_schema
    campaign.set_schema(manifest.schema_file)

    # setting up to use start_surveillance parameter as the broadcasting event and as the event to listen for
    # to trigger the vector surveillance

    add_broadcast_coordinator_event(campaign, broadcast_event=start_surveillance, start_day=5)
    add_broadcast_coordinator_event(campaign, broadcast_event=stop_surveillance, start_day=80)

    # Sample_Size distribution to be passed into the vector surveillance coordinator
    sample_size = Distributions.uniform(30, 100)

    """    Setting Up the Vector Surveillance Event Coordinator - Frequency_Counter
    distributed on day 0 of the simulation
    starts running when it is triggered start_surveillance event
    it runs every 3 days once triggered
    it samples 30-100 vectors of the species gambiae, gender female
    it has unique name of "Frequency_Counter" and it counts allele frequencies
    When done counting, it sends out the frequency_counter_ran whether or not dtk_vector_surveillance.py 
    sends out any other events
    
    The coordinator sends the data to the responder() function in the dtk_vector_surveillance.py,
    which runs on the same timestep as the coordinator and can send out coordinator-level events,
    based on the data it receives. 
    """
    add_vector_surveillance_event_coordinator(campaign, start_trigger_condition_list=[start_surveillance],
                                              stop_trigger_condition_list=[stop_surveillance],
                                              start_day=0, update_period=5, species="gambiae",
                                              sample_size=sample_size, survey_completed_event=frequency_counter_ran,
                                              gender=VectorGender.VECTOR_FEMALE,
                                              coordinator_name="Frequency_Counter", count_type=CountType.ALLELE_FREQ)

    """  Setting Up the Vector Surveillance Event Coordinator - Genome_Counter    
    distributed on day *2* of the simulation
    the duration of 20 means the event coordinator will be removed from the simulation whether 
    it's running or not on day (start_day + duration) 22
    starts running when it is triggered start_surveillance event
    it runs every *5* days once triggered
    it samples 30-100 vectors of the species gambiae, *both genders*
    it has unique name of "Genome_Counter" and it counts *GENOME_FRACTION*
    When done counting, it sends out the *genome_counter_ran* whether or not dtk_vector_surveillance.py 
    sends out any other events
    
    The coordinator sends the data to the responder() function in the dtk_vector_surveillance.py,
    which runs on the same timestep as the coordinator and can send out coordinator-level events,
    based on the data it receives. 
    """
    add_vector_surveillance_event_coordinator(campaign, start_trigger_condition_list=[start_surveillance],
                                              stop_trigger_condition_list=[stop_surveillance],
                                              start_day=2, update_period=5,
                                              duration=20, species="gambiae",
                                              sample_size=sample_size, survey_completed_event=genome_counter_ran,
                                              gender=VectorGender.VECTOR_BOTH_GENDERS,
                                              coordinator_name="Genome_Counter", count_type=CountType.GENOME_FRACTION)

    """ Release Mosquitoes when Frequency_Counter sends out release_a1 ("Release_More_Mosquitoes_a1a1") in respond()
    When the respond() function returns the COORDINATOR-LEVEL "Release_More_Mosquitoes_a1a1" event, this 
    TriggeredEventCoordinator (TEC) will distribute the MosquitoRelease intervention that is release 50,000 mosquitoes. 
    When it is done distributing the intervention, TriggeredEventCoordinator will broadcast the COORDINATOR-LEVEL 
    completion_event_a1 event.
    
    NOTE: The TriggeredEventCoordinator can distribute node- and individual- level interventions, you can pass in 
    one or a list of interventions. You cannot mix and match node- and individual- level interventions in the list.
    MosquitoRelease is a node-level intervention.
    """
    mosquito_release = _mosquito_release(campaign, released_number=50000, released_species="gambiae",
                                         released_genome=[["X", "X"], ["a1", "a1"], ["b0", "b0"]])
    add_triggered_coordinator_event(campaign, start_day=0, start_trigger_condition_list=[release_a1],
                                    node_interventions=mosquito_release, completion_event=completion_event_a1)

    """ Give out Ivermectin and Bednet interventions when Genome_Counter sends out release_ind_events 
         ("Release_ind_Events") in respond()
    When the respond() function returns the COORDINATOR-LEVEL "Release_ind_Events" event, this 
    TriggeredEventCoordinator (TEC) will distribute the Ivermectin and Bednet interventions to children under 10. 
    When it is done distributing the interventions, TriggeredEventCoordinator will broadcast the COORDINATOR-LEVEL 
    completion_event_ind event.

    NOTE: The TriggeredEventCoordinator can distribute node- and individual- level interventions, you can pass in 
    one or a list of interventions. You cannot mix and match node- and individual- level interventions in the list.
    Ivermectin and Bednet are individual-level interventions.
    """
    ivermectin = _ivermectin(campaign, killing_initial_effect=0.8, killing_box_duration=20,
                             killing_decay_time_constant=10)
    bednets = _simple_bednet(campaign, blocking_initial_effect=0.8, blocking_box_duration=20,
                             blocking_decay_time_constant=10, killing_initial_effect=0.8,
                             killing_box_duration=20, killing_decay_time_constant=10,
                             repelling_initial_effect=0.8, repelling_box_duration=20, repelling_decay_time_constant=10)

    add_triggered_coordinator_event(campaign, start_day=0, start_trigger_condition_list=[release_ind_events],
                                    demographic_coverage=0.5, completion_event=completion_event_ind,
                                    target_age_max=10, individual_interventions=[ivermectin, bednets])

    """ Give two MosquitoRelease interventions when Genome_Counter sends out release_a1b1  
                    ("Release_More_Mosquitoes_a1b1") in respond()
    When the respond() function returns the COORDINATOR-LEVEL "Release_More_Mosquitoes_a1b1" event, this 
    TriggeredEventCoordinator (TEC) will distribute the MosquitoRelease interventions.
    When it is done distributing the interventions, TriggeredEventCoordinator will broadcast the COORDINATOR-LEVEL 
    completion_event_b1 (DoneReleasing_b1b1) event.

    NOTE: The TriggeredEventCoordinator can distribute node- and individual- level interventions, you can pass in 
    one or a list of interventions. You cannot mix and match node- and individual- level interventions in the list.
    MosquitoRelease is a node-level intervention.
    """
    mosquito_release2 = _mosquito_release(campaign, released_number=10000, released_species="gambiae",
                                          released_genome=[["X", "X"], ["a0", "a0"], ["b0", "b0"]])
    mosquito_release3 = _mosquito_release(campaign, released_number=10000, released_species="gambiae",
                                          released_genome=[["X", "X"], ["a1", "a1"], ["b1", "b1"]])
    add_triggered_coordinator_event(campaign, start_day=0, start_trigger_condition_list=[release_a1b1],
                                    completion_event=completion_event_b1,
                                    node_interventions=[mosquito_release2, mosquito_release3])
    return campaign


def build_demog():
    """
        Builds demographics
    Returns:
        complete demographics
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    demog = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1)

    return demog


def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    experiment_name = "VectorSurveillance example"

    # create EMODTask 
    print("Creating EMODTask (from files)...")
    task = EMODTask.from_default2(
        config_path="my_config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_path=manifest.my_ep4_assets_dir,
        demog_builder=build_demog,
        plugin_report=None  # report
    )

    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)

    add_report_vector_genetics(task, manifest, species="gambiae")
    add_coordinator_event_recorder(task, event_list=[start_surveillance,
                                                     stop_surveillance,
                                                     completion_event_a1,
                                                     release_a1,
                                                     completion_event_ind,
                                                     release_ind_events,
                                                     frequency_counter_ran,
                                                     genome_counter_ran,
                                                     completion_event_b1,
                                                     release_a1b1])

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

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
