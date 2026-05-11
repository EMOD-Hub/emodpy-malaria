# SurveillanceEventCoordinator



The **SurveillanceEventCoordinator** coordinator class listens for and detects events happening and then responds with broadcasted events when a threshold has been met. This campaign
event is typically used with other classes, such as [BroadcastCoordinatorEvent](parameter-campaign-event-broadcastcoordinatorevent.md), [TriggeredEventCoordinator](parameter-campaign-event-triggeredeventcoordinator.md), and [DelayEventCoordinator](parameter-campaign-event-delayeventcoordinator.md).

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

{{ read_csv("csv/campaign-surveillanceeventcoordinator.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "comment": "Broadcast Event to start Surveillance",
            "class": "CampaignEvent",
            "Start_Day": 2,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "BroadcastCoordinatorEvent",
                "Coordinator_Name": "Coordnator_1",
                "Cost_To_Consumer": 10,
                "Broadcast_Event": "Start_ACF"
            }
        },
        {
            "comment": "Triggered by Broadcast_Event, stops itself by broadcasting Start_SIA_X Event",
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "SurveillanceEventCoordinator",
                "Coordinator_Name": "ACF_Counter",
                "Start_Trigger_Condition_List": [
                    "Start_ACF"
                ],
                "Stop_Trigger_Condition_List": [
                    "Start_SIA_2",
                    "Start_SIA_4"
                ],
                "Duration": 30,
                "Incidence_Counter": {
                    "Counter_Type": "PERIODIC",
                    "Counter_Period": 14,
                    "Counter_Event_Type": "NODE",
                    "Trigger_Condition_List": [
                        "Node_Event_1",
                        "Node_Event_2"
                    ],
                    "Node_Property_Restrictions": [],
                    "Property_Restrictions_Within_Node": [],
                    "Target_Demographic": "Everyone",
                    "Demographic_Coverage": 1.0
                },
                "Responder": {
                    "Responded_Event": "Respond_To_Surveillance",
                    "Threshold_Type": "COUNT",
                    "Action_List": [
                        {
                            "Threshold": 5,
                            "Event_Type": "COORDINATOR",
                            "Event_To_Broadcast": "Ind_Start_SIA_2"
                        },
                        {
                            "Threshold": 2,
                            "Event_Type": "COORDINATOR",
                            "Event_To_Broadcast": "Ind_Start_SIA_4"
                        }
                    ]
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 3,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "BroadcastNodeEvent",
                    "Cost_To_Consumer": 25,
                    "Broadcast_Event": "Node_Event_1"
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 3,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "BroadcastNodeEvent",
                    "Cost_To_Consumer": 25,
                    "Broadcast_Event": "Node_Event_1"
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 4,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "BroadcastNodeEvent",
                    "Cost_To_Consumer": 25,
                    "Broadcast_Event": "Node_Event_2"
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
