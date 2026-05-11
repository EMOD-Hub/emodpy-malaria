# BroadcastEvent


The **BroadcastEvent** intervention class is an individual-level class that immediately broadcasts
the event trigger you specify. This campaign event is typically used with other classes that monitor
for a broadcast event, such as [NodeLevelHealthTriggeredIV](parameter-campaign-node-nodelevelhealthtriggerediv.md) or
[CommunityHealthWorkerEventCoordinator](parameter-campaign-event-communityhealthworkereventcoordinator.md).

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

{{ read_csv("csv/campaign-broadcastevent.csv", keep_default_na=False) }}

```json
{
    "class": "CampaignEvent",
    "Start_Day": 0,
    "Nodeset_Config": {
        "class": "NodeSetAll"
    },
    "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Target_Demographic": "ExplicitAgeRanges",
        "Target_Age_Min": 0,
        "Target_Age_Max": 5,
        "Demographic_Coverage": 0.03,
        "Intervention_Config": {
            "class": "MultiInterventionDistributor",
            "Intervention_List": [
                {
                    "class": "SimpleBednet",
                    "Bednet_Type": "ITN",
                    "Cost_To_Consumer": 3.75,
                    "Blocking_Rate": 0.9,
                    "Killing_Rate": 0.6,
                    "Durability_Time_Profile": "DECAYDURABILITY",
                    "Primary_Decay_Time_Constant": 1460,
                    "Secondary_Decay_Time_Constant": 730
                },
                {
                    "class": "BroadcastEvent",
                    "Broadcast_Event": "Received_ITN"
                }
            ]
        }
    }
}
```
