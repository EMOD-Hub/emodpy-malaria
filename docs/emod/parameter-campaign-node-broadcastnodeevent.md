# BroadcastNodeEvent



The **BroadcastNodeEvent** node intervention class broadcasts node events. This can be used with the
campaign class, [SurveillanceEventCoordinator](parameter-campaign-event-surveillanceeventcoordinator.md), that can monitor and
listen for events received from **BroadcastNodeEvent** and then perform an action based on the
broadcasted event. You can also use this for the reporting of the broadcasted events by setting the
configuraton parameters, **Report_Node_Event_Recorder** and **Report_Surveillance_Event_Recorder**,
which listen to events to be recorded. You must use this coordinator class with listeners that are
operating on the same core. You can also use [NLHTIVNode](parameter-campaign-node-nlhtivnode.md).

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

{{ read_csv("csv/campaign-broadcastnodeevent.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.5,
                "Intervention_Config": {
                    "class": "OutbreakIndividual",
                    "Incubation_Period_Override": 0,
                    "Antigen": 0,
                    "Genome": 0
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 5,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [1]
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "BroadcastNodeEvent",
                    "Cost_To_Consumer": 10,
                    "Broadcast_Event": "Node_Event_1"
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 15,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [2, 3]
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "BroadcastNodeEvent",
                    "Cost_To_Consumer": 20,
                    "Broadcast_Event": "Node_Event_2"
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 25,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "BroadcastNodeEvent",
                    "Cost_To_Consumer": 25,
                    "Broadcast_Event": "Node_Event_3"
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
