# CampaignEvent


The **CampaignEvent** event class determines when to distribute the intervention based on the first day of
the simulation. See the following JSON example and table, which shows all available parameters for this
campaign event.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

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
