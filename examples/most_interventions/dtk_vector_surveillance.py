#!/usr/bin/python
"""
Embedded Python script required by VectorSurveillanceEventCoordinator.

EMOD calls respond() each time the coordinator samples the vector population.
The return value is a list of coordinator-level event names to broadcast.

This file must be placed in the simulation working directory alongside the
campaign and configuration files.
"""

import csv

header_written = []


def write_csv_report(time, coordinator_name, num_vectors_sampled,
                     list_data_names, list_data_values, filename=None):
    if not filename:
        filename = f"{coordinator_name}_py_log.csv"
    with open(filename, "a") as csv_log:
        line = f"{time}, {coordinator_name}, {num_vectors_sampled}"
        for val in list_data_values:
            line += f",{round(val, 5)}"
        if coordinator_name not in header_written:
            header = "time, coordinator_name, num_vectors_sampled"
            for name in list_data_names:
                header += f",{name}"
            csv_log.write(header + "\n")
            header_written.append(coordinator_name)
        csv_log.write(line + "\n")


def create_responder(responder_id, coordinator_name):
    print(f"py: creating responder: {responder_id} - {coordinator_name}")


def delete_responder(responder_id, coordinator_name):
    print(f"py: deleting responder: {responder_id} - {coordinator_name}")


def respond(time, responder_id, coordinator_name, num_vectors_sampled,
            list_data_names, list_data_values):
    event_names = ["VectorCoordinatorResponderEvent"]
    write_csv_report(time, coordinator_name, num_vectors_sampled,
                     list_data_names, list_data_values)
    return event_names
