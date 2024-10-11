#!/usr/bin/python

import os
import sys
import pandas as pd
import csv

"""
This is the embedded Python code that is used with the VectorSurveillanceEventCoordinator(VSEC).
The main purpose of this code is to determine if new Coordinator Evens should be broadcast
based on the vectors that were sampled.

The create and delete methods are available in case you want to create instances of the python
version of the responder that contain state.  For example, if you have several responders/VSECs
and your next decision was based on your previous, you might need each python responder to remember
what it last did.  In that case, you could create a python class and create a new one for each
instance of VSEC.

The "respond()" method is the main method called from VSEC.  It is called each time VSEC samples
the vectors.  You want to modify this method to do data evaluation as you see fit and add events to the
event_names list that will be broadcasted as coordinator-level events.  These events can be used to trigger
interventions in the campaign.  The events in the list should correspond to the events used in the campaign,
if they do not, the simulation will fail.

responder_id - Each responder gets a unique ID.  this allows you to tell each one apart. The ids are assigned
in order of VSEC creation.

coordinator_name - This the name of the VSEC that owns the responder.  You could have multiple
    instances of VSEC's with the same name, but they will still have unique responder_ids.  
    However, giving VSECs a unique name allows you to easily differentiate between them in the respond() function.
    Because coordinator_name is static while responder_id is created dynamically, it is best to use unique 
    coordinator_names to differentiate between VSECs.
    
"""
header_not_needed = []


def write_csv_report(time, coordinator_name, num_vectors_sampled, list_data_names, list_data_values, filename=None):
    """
        Write a csv report with the data passed in.
        This assumes that order of names in list_data_names is always the same and always the same length.
        (which is true)
        If the file does not exist, it will be created.
        The data is gotten from "respond()" which gets it from EMOD.

        NOTE: You could create a class called SurveillanceReport and created an object for each instance of VSEC.
        The object could have kept track of the file name and whether the header was created for that instance.

    Args:
        time: timestamp of the data
        coordinator_name: unique name of the coordinator
        num_vectors_sampled: number of vectors that were used for this data
        list_data_names: list of names of alleles or genes possible in the vector population
        list_data_values: list of the fraction of each allele or gene in the vector population matching the
            location in list_data_names
        filename: name of the file to write to.  If None, it will write to "<coordinator_name>_py_log.csv"

    Returns:
        Nothing
    """
    if not filename:
        filename = f"{coordinator_name}_py_log.csv"
    with open(filename, "a") as csv_log:
        line = f"{time}, {coordinator_name}, {num_vectors_sampled}"
        for i in range(len(list_data_values)):
            line += f",{round(list_data_values[i], 5)}"
        if coordinator_name not in header_not_needed:  # write header: this is the first time us seeing this coordinator
            header = "time, coordinator_name, num_vectors_sampled"
            for i in range(len(list_data_names)):
                header += f",{list_data_names[i]}"
            csv_log.write(header + "\n")
            header_not_needed.append(coordinator_name)  # add coordinator name to the list, so we don't do it again
        csv_log.write(line + "\n")


def create_responder(responder_id, coordinator_name):
    # this function is called when VectorSurveillanceEventCoordinator is created and can be used to
    # initialize objects or states for the duration of a simulation run
    print(f"py: creating responder: {responder_id} - {coordinator_name}")


def delete_responder(responder_id, coordinator_name):
    print(f"py: deleting responder: {responder_id} - {coordinator_name}")
    # this is where you would do any cleanup if you had any
    # currently writing files from here does not work, will investigate.


def respond(time, responder_id, coordinator_name, num_vectors_sampled, list_data_names, list_data_values):
    """
        This is a static method called each time a VectorSurveillanceEventCoordinator samples the vectors.
        If you want to have different response logic depending on the coordinator, you will need to use the
        coordinator's name and/or responder_id to call that logic for the given VSEC.

        Surveillance results are two lists: list_data_names and list_data_values. The list_data_names list contains the
        names of all the alleles present (when CountType.ALLELE_FREQ) or genomes possible (when CountType.GENOME_FRACTION)
        in the vector population. The list_data_values list contains either the fraction of each of the alleles at its
        locus of the vectors sampled (when CountType.ALLELE_FREQ) or the fraction of each of the genomes in the vectors
        sampled (when CountType.GENOME_FRACTION).

        The respond() function in dtk_vector_surveillance.py is called each time any VectorSurveillanceEventCoordinator
        samples the vectors. The respond() function receives following info from the VectorSurveillanceEventCoordinator:
        time, responder_id, coordinator_name, num_vectors_sampled, list_data_names, list_data_values
        You can write any code you want in the respond() function to process the data, using coordinator_name to
        differentiate between different VectorSurveillanceEventCoordinators. The respond() function returns a list of
        event names to be broadcast as coordinator-level events. The events are added by you based on processing of
        sampled vectors' data. These events can be used to trigger interventions in the campaign. The events in the
        list should correspond to the events used in the campaign, if they are not, the simulation will fail unless
        they are manually added to the config.parameters.Custom_Coordinator_Events.

    Args:
        time: time of the sampling
        responder_id: unique id of the responder, generated when VectorSurveillanceEventCoordinator is created
        coordinator_name: unique name of the coordinator
        num_vectors_sampled: number of vectors that were sampled
        list_data_names: The list_data_names list contains the
            names of all the alleles present (when CountType.ALLELE_FREQ) or genomes possible
            (when CountType.GENOME_FRACTION) in the vector population.
        list_data_values: list that contains either the fraction of each of the alleles at its
            locus of the vectors sampled (when CountType.ALLELE_FREQ) or the fraction of each of the genomes in the
            vectors sampled (when CountType.GENOME_FRACTION). Note: genomes are grouped by

    Returns:
        list of event names to broadcast as coordinator-level events
        Note: these events should correspond to the events used in the campaign, otherwise the simulation will fail
        unless they are manually added to the config.parameters.Custom_Coordinator_Events.
    """

    event_names = []  # every string added to this will be sent out as a coordinator-level event
    if coordinator_name == "Frequency_Counter":
        # here we are dealing with allele frequencies
        # straightforward "loop through and when find something, do something"
        # this is limiting, because we are only looking at one parameter at a time
        for i in range(len(list_data_names)):
            if (list_data_names[i] == "a1") and (list_data_values[i] < 0.3):
                event_names.append("Release_More_Mosquitoes_a1a1")
        # calling the write_csv_report function to write the data to a csv file
        write_csv_report(time=time, coordinator_name=coordinator_name, num_vectors_sampled=num_vectors_sampled,
                         list_data_names=list_data_names, list_data_values=list_data_values,
                         filename="freq_log.csv")

    elif coordinator_name == "Genome_Counter":
        write_csv_report(time=time, coordinator_name=coordinator_name, num_vectors_sampled=num_vectors_sampled,
                         list_data_names=list_data_names, list_data_values=list_data_values)
        # this is a more robust way to do this, because we can look at multiple parameters at once
        # another way to do this by making allele_combos keys in dictionary of fraction values
        # this makes it easier to make more complex logic combinations
        data = dict(zip(list_data_names, list_data_values))
        genome1 = "X-a0-b0:X-a0-b0"
        genome2 = "X-a0-b1:X-a0-b1"
        genome3 = "X-a0-b0:X-a0-b1"  # this is grouped with "X-a0-b1:X-a0-b0"
        if data[genome1] > 0.4:
            event_names.append("Release_ind_Events")
        if data[genome3] > data[genome2] or data[genome2] > 0.03:
            event_names.append("Release_More_Mosquitoes_a1b1")

    return event_names
