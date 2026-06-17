# VectorSurveillanceEventCoordinator


The **VectorSurveillanceEventCoordinator** coordinator class samples the vector population
at regular intervals and reports allele frequencies or genome fractions. This coordinator is 
designed to simulate vector surveillance activities such as mosquito trapping and genetic testing, 
and to trigger campaign events based on the results. It is configured with
a **Counter** object that specifies the species, gender, sample size, and counting method, and
a **Responder** object that can broadcast an event each time a survey is completed. Sampling
is controlled by trigger events: the coordinator begins sampling when an event from
**Start_Trigger_Condition_List** is received, and stops when an event from
**Stop_Trigger_Condition_List** is received or the **Duration** expires.

The coordinator delegates its response logic to an embedded Python script,
**dtk_vector_surveillance.py**, which must be placed in the simulation working directory.
Each time the coordinator samples the vector population, it calls the ``respond()`` function
in this script, passing the sampled data. The ``respond()`` function processes the data and
returns a list of coordinator-level event names to broadcast. These events can then trigger
other campaign events such as mosquito releases or intervention distributions.

## Embedded Python: dtk_vector_surveillance.py

The **dtk_vector_surveillance.py** file provides three callback functions that the
**VectorSurveillanceEventCoordinator** calls during the simulation. The file must be placed
in the simulation working directory alongside the campaign and configuration files.

### Required function: ``respond()``

```python
def respond(time, responder_id, coordinator_name, num_vectors_sampled, list_data_names, list_data_values):
```

This is the main callback, called each time any **VectorSurveillanceEventCoordinator** in the
simulation completes a sampling event. It receives the surveillance results and must return
a list of coordinator-level event name strings to broadcast. If no events should be broadcast,
return an empty list.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| ``time`` | float | The simulation time (in days) when the sampling occurred. |
| ``responder_id`` | int | A unique integer ID assigned to this responder instance when the coordinator was created. IDs are assigned in order of coordinator creation. |
| ``coordinator_name`` | string | The **Coordinator_Name** of the **VectorSurveillanceEventCoordinator** that performed this sampling. Use this to differentiate between multiple coordinators. |
| ``num_vectors_sampled`` | int | The number of vectors that were actually sampled (may be less than requested if the population is small). |
| ``list_data_names`` | list[str] | When **Count_Type** is ``ALLELE_FREQ``: a list of all allele names present in the vector population (e.g., ``["a0", "a1"]``). When **Count_Type** is ``GENOME_FRACTION``: a list of all possible genome strings (e.g., ``["X-a0:X-a0", "X-a0:X-a1", "X-a1:X-a1"]``). Genomes that are equivalent under allele reordering are grouped together. |
| ``list_data_values`` | list[float] | The fraction corresponding to each entry in ``list_data_names``. When **Count_Type** is ``ALLELE_FREQ``: the frequency of each allele at its locus in the sampled population (accounts for two allele copies per vector). When **Count_Type** is ``GENOME_FRACTION``: the fraction of each genome in the sampled population. |

**Returns:** A ``list[str]`` of coordinator-level event names to broadcast. These events must
correspond to events used in the campaign file or be defined in
**Custom_Coordinator_Events** in the simulation configuration. If an event name is not
recognized, the simulation will fail.

!!! note
    Because all **VectorSurveillanceEventCoordinator** instances in the simulation share the
    same ``respond()`` function, use the ``coordinator_name`` parameter to route logic to the
    correct coordinator. Assign unique **Coordinator_Name** values to each coordinator instance
    to make this straightforward.

### Optional function: ``create_responder()``

```python
def create_responder(responder_id, coordinator_name):
```

Called once when each **VectorSurveillanceEventCoordinator** is created. Use this to
initialize any per-coordinator state (e.g., creating Python objects, opening log files).
If your ``respond()`` function is stateless, this function can be a no-op or omitted.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| ``responder_id`` | int | The unique ID assigned to this responder instance. |
| ``coordinator_name`` | string | The **Coordinator_Name** of the coordinator being created. |

### Optional function: ``delete_responder()``

```python
def delete_responder(responder_id, coordinator_name):
```

Called when a **VectorSurveillanceEventCoordinator** expires (after **Duration** elapses).
Use this for cleanup of per-coordinator state. If your ``respond()`` function is stateless,
this function can be a no-op or omitted.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| ``responder_id`` | int | The unique ID of the responder being deleted. |
| ``coordinator_name`` | string | The **Coordinator_Name** of the coordinator being deleted. |

### Example: dtk_vector_surveillance.py

The following example demonstrates a ``dtk_vector_surveillance.py`` that handles two
coordinators: one monitoring allele frequencies (``Frequency_Counter``) and one monitoring
genome fractions (``Genome_Counter``). It writes CSV logs of the surveillance data and
broadcasts events to trigger mosquito releases when certain thresholds are met.

```python
#!/usr/bin/python

import csv

header_not_needed = []


def write_csv_report(time, coordinator_name, num_vectors_sampled,
                     list_data_names, list_data_values, filename=None):
    """Write surveillance data to a CSV file, creating the header on first call."""
    if not filename:
        filename = f"{coordinator_name}_py_log.csv"
    with open(filename, "a") as csv_log:
        line = f"{time}, {coordinator_name}, {num_vectors_sampled}"
        for i in range(len(list_data_values)):
            line += f",{round(list_data_values[i], 5)}"
        if coordinator_name not in header_not_needed:
            header = "time, coordinator_name, num_vectors_sampled"
            for i in range(len(list_data_names)):
                header += f",{list_data_names[i]}"
            csv_log.write(header + "\n")
            header_not_needed.append(coordinator_name)
        csv_log.write(line + "\n")


def create_responder(responder_id, coordinator_name):
    # Called when VectorSurveillanceEventCoordinator is created.
    # Initialize per-coordinator state here if needed.
    print(f"py: creating responder: {responder_id} - {coordinator_name}")


def delete_responder(responder_id, coordinator_name):
    # Called when VectorSurveillanceEventCoordinator expires.
    # Clean up per-coordinator state here if needed.
    print(f"py: deleting responder: {responder_id} - {coordinator_name}")


def respond(time, responder_id, coordinator_name, num_vectors_sampled,
            list_data_names, list_data_values):
    """
    Called each time any VectorSurveillanceEventCoordinator samples the vectors.
    Returns a list of coordinator-level event names to broadcast.
    """
    event_names = []

    if coordinator_name == "Frequency_Counter":
        # ALLELE_FREQ mode: check individual allele frequencies
        for i in range(len(list_data_names)):
            if (list_data_names[i] == "a1") and (list_data_values[i] < 0.3):
                event_names.append("Release_More_Mosquitoes_a1a1")
        write_csv_report(time, coordinator_name, num_vectors_sampled,
                         list_data_names, list_data_values, filename="freq_log.csv")

    elif coordinator_name == "Genome_Counter":
        # GENOME_FRACTION mode: use a dict for multi-genome threshold logic
        write_csv_report(time, coordinator_name, num_vectors_sampled,
                         list_data_names, list_data_values)
        data = dict(zip(list_data_names, list_data_values))
        genome1 = "X-a0-b0:X-a0-b0"
        genome2 = "X-a0-b1:X-a0-b1"
        genome3 = "X-a0-b0:X-a0-b1"  # grouped with "X-a0-b1:X-a0-b0"
        if data[genome1] > 0.4:
            event_names.append("Release_ind_Events")
        if data[genome3] > data[genome2] or data[genome2] > 0.03:
            event_names.append("Release_More_Mosquitoes_a1b1")

    return event_names
```

## Parameters

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv("csv/campaign-vectorsurveillanceeventcoordinator.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "VectorSurveillanceEventCoordinator",
                "Coordinator_Name": "Allele_Frequency_Monitor",
                "Duration": -1,
                "Start_Trigger_Condition_List": [
                    "Start_Vector_Surveillance"
                ],
                "Stop_Trigger_Condition_List": [],
                "Counter": {
                    "Count_Type": "ALLELE_FREQ",
                    "Species": "gambiae",
                    "Gender": "VECTOR_FEMALE",
                    "Sample_Size_Distribution": "CONSTANT_DISTRIBUTION",
                    "Sample_Size_Constant": 100,
                    "Update_Period": 30
                },
                "Responder": {
                    "Survey_Completed_Event": "Vector_Survey_Done"
                }
            }
        }
    ]
}
```
