# DelayEventCoordinator



The **DelayEventCoordinator** coordinator class insert delays into coordinator event chains. This campaign
event is typically used with [BroadcastCoordinatorEvent](parameter-campaign-event-broadcastcoordinatorevent.md) to broadcast events after the delays.

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

{{ read_csv("csv/campaign-delayeventcoordinator.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "comment": "Trigger to start Delay",
            "class": "CampaignEvent",
            "Start_Day": 2,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "BroadcastCoordinatorEvent",
                "Coordinator_Name": "Coordnator_1",
                "Cost_To_Consumer": 10,
                "Broadcast_Event": "Coordinator_Event_1"
            }
        },
        {
            "comment": "restart Delay",
            "class": "CampaignEvent",
            "Start_Day": 10,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "BroadcastCoordinatorEvent",
                "Coordinator_Name": "Coordnator_1",
                "Cost_To_Consumer": 10,
                "Broadcast_Event": "Coordinator_Event_1"
            }
        },
        {
            "comment": "Delay",
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Target_Demographic": "Everyone",
            "Event_Coordinator_Config": {
                "class": "DelayEventCoordinator",
                "Coordinator_Name": "DelayEventCoordinator_10",
                "Start_Trigger_Condition_List": [
                    "Coordinator_Event_1"
                ],
                "Stop_Trigger_Condition_List": [],
                "Duration": 100,
                "Delay_Period_Distribution": "CONSTANT_DISTRIBUTION",
                "Delay_Period_Constant": 25,
                "Delay_Complete_Event": "Completion_Delayed_Coordinator_Event_1"
            }
        }
    ],
    "Use_Defaults": 1
}
```
