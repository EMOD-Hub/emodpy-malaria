# NChooserEventCoordinator


The **NChooserEventCoordinator** coordinator class is used to distribute an individual-level intervention to
exactly N people of a targeted demographic. This contrasts with other event coordinators that
distribute an intervention to a percentage of the population, not to an exact count. See the
following JSON example and table, which shows all available parameters for this event coordinator.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-nchoosereventcoordinator.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 1,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config__KP1": "",
        "Event_Coordinator_Config": {
            "class": "NChooserEventCoordinator",
            "Distributions": [{
                "Start_Day": 10,
                "End_Day": 11,
                "Property_Restrictions_Within_Node": [{
                    "QualityOfCare": "Bad"
                }],
                "Age_Ranges_Years": [{
                    "Min": 20,
                    "Max": 40
                }],
                "Num_Targeted": [
                    99999999
                ]
            }],
            "Intervention_Config": {
                "class": "ControlledVaccine",
                "Cost_To_Consumer": 10,
                "Vaccine_Type": "AcquisitionBlocking",
                "Vaccine_Take": 1.0,
                "Waning_Config": {
                    "class": "WaningEffectMapLinear",
                    "Initial_Effect": 1.0,
                    "Expire_At_Durability_Map_End": 1,
                    "Durability_Map": {
                        "Times": [
                            0,
                            50,
                            100
                        ],
                        "Values": [
                            1.0,
                            1.0,
                            0.0
                        ]
                    }
                },
                "Distributed_Event_Trigger": "Vaccinated",
                "Expired_Event_Trigger": "VaccineExpired",
                "Duration_To_Wait_Before_Revaccination": 0
            }
        }
    }]
}
```
