# BroadcastEvent


The **BroadcastEvent** intervention class is an individual-level class that immediately broadcasts
the event trigger you specify. This campaign event is typically used with other classes that monitor
for a broadcast event, such as [parameter-campaign-node-nodelevelhealthtriggerediv](parameter-campaign-node-nodelevelhealthtriggerediv.md) or
[parameter-campaign-event-communityhealthworkereventcoordinator](parameter-campaign-event-communityhealthworkereventcoordinator.md).

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
