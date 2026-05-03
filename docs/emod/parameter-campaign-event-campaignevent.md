# CampaignEvent


The **CampaignEvent** event class determines when to distribute the intervention based on the first day of
the simulation. See the following JSON example and table, which shows all available parameters for this
campaign event.

.. note::

    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    |EMOD_s| does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with |EMOD_s| will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not |EMOD_s| parameter names will be ignored by the
    model.

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv("csv/campaign-campaignevent.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Event_Name": "Individual outbreak",
        "Start_Day": 1,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 1.0,
            "Intervention_Config": {
                "class": "OutbreakIndividual"
            }
        }
    }]
}
```


## Nodeset_Config classes


The following classes determine in which nodes the event will occur.

### NodeSetAll


The event will occur in all nodes in the simulation. This class has no associated parameters. For example,

```json
{
    "Nodeset_Config": {
        "class": "NodeSetAll"
    }
}
```

### NodeSetNodeList


The event will occur in the nodes listed by Node ID.

{{ read_csv("csv/campaign-nodesetnodelist.csv") }}

### NodeSetPolygon


The event will occur in the nodes that fall within a given polygon.

{{ read_csv("csv/campaign-nodesetpolygon.csv") }}
