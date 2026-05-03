# BroadcastCoordinatorEventFromNode



The **BroadcastCoordinatorEventFromNode** is node-level intervention that broadcasts 
an event for coordinators. For example, if a death occurs in a node, an event can be 
broadcasted that will trigger some sort of response by the healthcare system. 
**NodeLevelHealthTriggeredIV** could be used to listen for the death of an individual and 
distribute this intervention to the node. The node intervention could then broadcast its event 
that a **TriggeredEventCoordinator** is listening for. One can use the 
**Report_Coordinator_Event_Recorder** to report on the events broadcasted by this intervention. 
Note, this coordinator class must be used with listeners that are operating on the same core. 

For more information, see [emod:dev-architecture-core](emod:dev-architecture-core.md).

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-broadcastcoordinatoreventfromnode.csv") }}

```json
{
    "Events": [
        {
            "class": "CampaignEventByYear",
            "Start_Year": 1990.0,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": [
                        "NonDiseaseDeaths",
                        "DiseaseDeaths"
                    ],
                    "Demographic_Coverage": 1.0,
                    "Actual_NodeIntervention_Config": {
                        "class": "BroadcastCoordinatorEventFromNode",
                        "Broadcast_Event" : "Distribute_Vaccine"
                    }
                }
            }
        },
        {
            "class": "CampaignEventByYear",
            "Start_Year": 1990.0,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "TriggeredEventCoordinator",
                "Coordinator_Name": "VaccineDistributor",
                "Start_Trigger_Condition_List": [ "Distribute_Vaccine" ],
                "Stop_Trigger_Condition_List": [],
                "Number_Repetitions": 1,
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.5,
                "Intervention_Config": {
                    "class": "SimpleVaccine",
                    "Cost_To_Consumer": 2,
                    "Vaccine_Take": 1,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Initial_Effect": 1.0,
                        "Box_Duration": 100
                    }
                },
                "Completion_Event": "Vaccine_Was_Distributed"
            }
        }
    ],
    "Use_Defaults": 1
}
```
