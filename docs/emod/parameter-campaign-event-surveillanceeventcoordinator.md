# SurveillanceEventCoordinator


The **SurveillanceEventCoordinator** extends the
[IncidenceEventCoordinator](parameter-campaign-event-incidenceeventcoordinator.md) by adding
start/stop trigger events, a configurable duration, and periodic counting. It monitors for
coordinator-level start events, begins counting individual, node, or coordinator events using a
periodic **Incidence_Counter**, and responds via a **Responder** when counting periods complete.

The coordinator remains dormant until it receives a start trigger event from the
**Start_Trigger_Condition_List**. Once started, it operates in a periodic count-respond cycle:

1. The **Incidence_Counter** counts events of the type specified by **Counter_Event_Type**
   (individual, node, or coordinator) during each **Counter_Period** (in days). Only events
   matching the **Trigger_Condition_List** and demographic/property restrictions are counted.
2. At the end of each counter period, the **Responder** calculates the incidence value as a raw
   count, percentage, or percentage of events (based on **Threshold_Type**).
3. The responder selects the action from **Action_List** whose **Threshold** is the highest value
   that is still less than or equal to the calculated incidence.
4. The selected action's **Event_To_Broadcast** event is broadcast. If **Responded_Event** is set,
   it is also broadcast as a coordinator event after the action event.
5. The counter resets and begins the next period, continuing until a stop event is received or the
   **Duration** expires.

The coordinator can be stopped by an event in **Stop_Trigger_Condition_List** and restarted by a
subsequent start trigger event. The coordinator does not expire until its **Duration** has elapsed.

This coordinator is typically used with other classes such as
[BroadcastCoordinatorEvent](parameter-campaign-event-broadcastcoordinatorevent.md),
[TriggeredEventCoordinator](parameter-campaign-event-triggeredeventcoordinator.md), and
[DelayEventCoordinator](parameter-campaign-event-delayeventcoordinator.md).

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.

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
    "Use_Defaults": 1,
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
                "Coordinator_Name": "Coordinator_1",
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
                "Duration": 30,
                "Start_Trigger_Condition_List": [
                    "Start_ACF"
                ],
                "Stop_Trigger_Condition_List": [
                    "Start_SIA_2",
                    "Start_SIA_4"
                ],
                "Incidence_Counter": {
                    "Counter_Type": "PERIODIC",
                    "Counter_Period": 14,
                    "Counter_Event_Type": "NODE",
                    "Trigger_Condition_List": [
                        "Node_Event_1",
                        "Node_Event_2"
                    ],
                    "Target_Demographic": "Everyone",
                    "Demographic_Coverage": 1.0
                },
                "Responder": {
                    "Responded_Event": "Respond_To_Surveillance",
                    "Threshold_Type": "COUNT",
                    "Action_List": [
                        {
                            "Threshold": 2,
                            "Event_Type": "COORDINATOR",
                            "Event_To_Broadcast": "Start_SIA_4"
                        },
                        {
                            "Threshold": 5,
                            "Event_Type": "COORDINATOR",
                            "Event_To_Broadcast": "Start_SIA_2"
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
    ]
}
```
