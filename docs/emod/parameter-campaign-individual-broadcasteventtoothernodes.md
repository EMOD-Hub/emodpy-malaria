# BroadcastEventToOtherNodes


The **BroadcastEventToOtherNodes** intervention class allows events to be sent from one node to
another. For example, if an individual in one node has been diagnosed, drugs may be
distributed to individuals in surrounding nodes.

When this intervention is updated, the event to be broadcast is cached to be distributed to the
nodes. After the people have migrated, the event information is distributed to the nodes (i.e. it
does support multi-core). During the next time step, the nodes will update their node-level
interventions and then broadcast the events from other nodes to ALL the people in the node. This is
different from interventions that only broadcast the event in the current node for the person
who had the intervention. Distances between nodes use the Longitude and Latitude defined in the
demographics file, and use the Haversine Formula for calculating the great-circle distance.

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

{{ read_csv("csv/campaign-broadcasteventtoothernodes.csv") }}

[link](../json/parameter-campaign-individual-broadcasteventtoothernodes.json)
