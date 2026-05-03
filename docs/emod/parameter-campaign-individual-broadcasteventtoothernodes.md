# BroadcastEventToOtherNodes


The **BroadcastEventToOtherNodes** intervention class allows events to be sent from one node to
another. For example, if an individual in one node has been diagnosed, drugs may be
distributed to individuals in surrounding nodes.

When this intervention is updated, the event to be broadcast is cached to be distributed to the
nodes. After the people have migrated, the event information is distributed to the nodes (i.e. it
does support multi-core). During the next time step, the nodes will update their node-level
interventions and then broadcast the events from other nodes to ALL the people in the node. This is
different from interventions that only broadcast the event in the current node for the person
who had the intervention. Distances between nodes use the Longitude and Latitude defined in the
demographics file, and use the Haversine Formula for calculating the great-circle distance.

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

{{ read_csv("csv/campaign-broadcasteventtoothernodes.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
            "Event_Name": "Broadcast to Other Households If Person Infected",
            "class": "CampaignEvent",
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Demographic_Coverage": 1,
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": ["NewClinicalCase"],
                    "Blackout_Event_Trigger": "Blackout",
                    "Blackout_Period": 0.0,
                    "Blackout_On_First_Occurrence": 0,
                    "Actual_IndividualIntervention_Config": {
                        "class": "BroadcastEventToOtherNodes",
                        "Event_Trigger": "VaccinateNeighbors",
                        "Include_My_Node": 1,
                        "Node_Selection_Type": "DISTANCE_AND_MIGRATION",
                        "Max_Distance_To_Other_Nodes_Km": 1
                    }
                }
            }
        },
        {
            "Event_Name": "Get Vaccinated If Neighbor Infected",
            "class": "CampaignEvent",
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Demographic_Coverage": 1,
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": ["VaccinateNeighbors"],
                    "Blackout_Event_Trigger": "Blackout",
                    "Blackout_Period": 0.0,
                    "Blackout_On_First_Occurrence": 0,
                    "Actual_IndividualIntervention_Config": {
                        "class": "AntimalarialDrug",
                        "Cost_To_Consumer": 10,
                        "Dosing_Type": "FullTreatmentParasiteDetect",
                        "Drug_Type": "Chloroquine",
                        "Dont_Allow_Duplicates": 1
                    }
                }
            }
        }
    ]
}
```
