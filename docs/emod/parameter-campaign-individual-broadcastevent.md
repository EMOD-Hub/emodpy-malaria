# BroadcastEvent


The **BroadcastEvent** intervention class is an individual-level class that immediately broadcasts
the event trigger you specify. This campaign event is typically used with other classes that monitor
for a broadcast event, such as [parameter-campaign-node-nodelevelhealthtriggerediv](parameter-campaign-node-nodelevelhealthtriggerediv.md) or
[parameter-campaign-event-communityhealthworkereventcoordinator](parameter-campaign-event-communityhealthworkereventcoordinator.md).

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-broadcastevent.csv") }}

```json
{
    "Event_Coordinator_Config": {
        "Demographic_Coverage": 0.03,
        "Intervention_Config": {
            "Intervention_List": [{
                    "Bednet_Type": "ITN",
                    "Blocking_Rate": 0.9,
                    "Cost_To_Consumer": 3.75,
                    "Durability_Time_Profile": "DECAYDURABILITY",
                    "Killing_Rate": 0.6,
                    "Primary_Decay_Time_Constant": 1460,
                    "Secondary_Decay_Time_Constant": 730,
                    "class": "SimpleBednet"
                },
                {
                    "Broadcast_Event": "Received_ITN",
                    "class": "BroadcastEvent"
                }
            ],
            "class": "MultiInterventionDistributor"
        },
        "Target_Age_Max": 5,
        "Target_Age_Min": 0,
        "Target_Demographic": "ExplicitAgeRanges",
        "class": "StandardInterventionDistributionEventCoordinator"
    },
    "Nodeset_Config": {
        "class": "NodeSetAll"
    },
    "Start_Day": 0,
    "class": "CampaignEvent"
}
```
