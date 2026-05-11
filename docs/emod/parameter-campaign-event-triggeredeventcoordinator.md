# TriggeredEventCoordinator



The **TriggeredEventCoordinator** coordinator class listens for trigger events, begins a series of repetitions of intervention distributions, and then broadcasts an event upon completion. This campaign
event is typically used with other classes that broadcast and distribute events, such as
[BroadcastCoordinatorEvent](parameter-campaign-event-broadcastcoordinatorevent.md), [DelayEventCoordinator](parameter-campaign-event-delayeventcoordinator.md), and [SurveillanceEventCoordinator](parameter-campaign-event-surveillanceeventcoordinator.md).

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

{{ read_csv("csv/campaign-triggeredeventcoordinator.csv", keep_default_na=False) }}

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
                "Demographic_Coverage": 0.25,
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
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [1, 2]
            },
            "Event_Coordinator_Config": {
                "class": "TriggeredEventCoordinator",
                "Coordinator_Name": "1n2_Vaccinator",
                "Start_Trigger_Condition_List": [
                    "Start_Vaccinating_1n2"
                ],
                "Stop_Trigger_Condition_List": [],
                "Number_Repetitions": 1,
                "Timesteps_Between_Repetitions": 1,
                "Duration": -1,
                "Target_Demographic": "Everyone",
                "Node_Property_Restrictions": [],
                "Property_Restrictions_Within_Node": [],
                "Demographic_Coverage": 0.05,
                "Intervention_Config": {
                    "class": "SimpleVaccine",
                    "Cost_To_Consumer": 1,
                    "Vaccine_Take": 1,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Initial_Effect": 0.59,
                        "Box_Duration": 730
                    }
                },
                "Completion_Event": "Done_Vaccinating_1n2"
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [1, 2]
            },
            "Event_Coordinator_Config": {
                "class": "TriggeredEventCoordinator",
                "Coordinator_Name": "1n2_Party",
                "Start_Trigger_Condition_List": [
                    "Done_Vaccinating_1n2"
                ],
                "Stop_Trigger_Condition_List": [],
                "Number_Repetitions": 1,
                "Timesteps_Between_Repetitions": 1,
                "Duration": -1,
                "Target_Demographic": "Everyone",
                "Node_Property_Restrictions": [],
                "Property_Restrictions_Within_Node": [],
                "Demographic_Coverage": 0.05,
                "Intervention_Config": {
                    "class": "BroadcastEvent",
                    "Cost_To_Consumer": 1,
                    "Broadcast_Event": "Individual_Celebrate_1n2"
                },
                "Completion_Event": "Done_Celebrating_1n2"
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [3, 4]
            },
            "Event_Coordinator_Config": {
                "class": "TriggeredEventCoordinator",
                "Coordinator_Name": "3n4_Party",
                "Start_Trigger_Condition_List": [
                    "Done_Vaccinating_3n4"
                ],
                "Stop_Trigger_Condition_List": [],
                "Number_Repetitions": 1,
                "Timesteps_Between_Repetitions": 1,
                "Duration": -1,
                "Target_Demographic": "Everyone",
                "Node_Property_Restrictions": [],
                "Property_Restrictions_Within_Node": [],
                "Demographic_Coverage": 0.05,
                "Intervention_Config": {
                    "class": "BroadcastEvent",
                    "Cost_To_Consumer": 1,
                    "Broadcast_Event": "Individual_Celebrate_3n4"
                },
                "Completion_Event": "Done_Celebrating_3n4"
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [3, 4]
            },
            "Event_Coordinator_Config": {
                "class": "TriggeredEventCoordinator",
                "Coordinator_Name": "3n4_Vaccinator",
                "Start_Trigger_Condition_List": [
                    "Start_Vaccinating_3n4"
                ],
                "Stop_Trigger_Condition_List": [
                    "Stop_Vaccinating_3n4"
                ],
                "Number_Repetitions": 1,
                "Timesteps_Between_Repetitions": 11,
                "Duration": -1,
                "Target_Demographic": "Everyone",
                "Node_Property_Restrictions": [],
                "Property_Restrictions_Within_Node": [],
                "Demographic_Coverage": 0.05,
                "Intervention_Config": {
                    "class": "SimpleVaccine",
                    "Cost_To_Consumer": 2,
                    "Vaccine_Take": 1,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Initial_Effect": 0.59,
                        "Box_Duration": 730
                    }
                },
                "Completion_Event": "Done_Vaccinating_3n4"
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 5,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [1, 2]
            },
            "Event_Coordinator_Config": {
                "class": "BroadcastCoordinatorEvent",
                "Coordinator_Name": "Start_Coordnator_1n2",
                "Cost_To_Consumer": 100,
                "Broadcast_Event": "Start_Vaccinating_1n2"
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 20,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [3, 4]
            },
            "Event_Coordinator_Config": {
                "class": "BroadcastCoordinatorEvent",
                "Coordinator_Name": "Start_Coordnator_3n4",
                "Cost_To_Consumer": 200,
                "Broadcast_Event": "Start_Vaccinating_3n4"
            }
        }
    ],
    "Use_Defaults": 1
}
```
