# BirthTriggeredIV


Note: This intervention has been replaced by NodeLevelHealthTriggeredIV, which provides more flexibility and can be
triggered by any individual event, including **Births** which mimics the BirthTriggeredIV. BirthTriggeredIV will
continue to be supported for backward compatibility but will not receive new features.

The **BirthTriggeredIV** intervention class listens for births in a node and distributes
an individual-level intervention to each newborn. It is a node-level intervention that persists
on the node for the specified **Duration** (or indefinitely if set to -1), distributing the
configured **Actual_IndividualIntervention_Config** to qualifying newborns based on demographic
targeting and property restrictions.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-birthtriggerediv.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 1,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "BirthTriggeredIV",
                "Duration": -1,
                "Demographic_Coverage": 0.95,
                "Target_Demographic": "Everyone",
                "Actual_IndividualIntervention_Config": {
                    "class": "SimpleVaccine",
                    "Cost_To_Consumer": 10,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Waning_Config": {
                        "class": "WaningEffectExponential",
                        "Decay_Time_Constant": 365,
                        "Initial_Effect": 0.8
                    }
                }
            }
        }
    }]
}
```
