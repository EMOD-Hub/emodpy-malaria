# ImmunityBloodTest


The **ImmunityBloodTest** intervention class identifies whether an individual's immunity meets a
specified threshold (as set with the **Positive_Threshold_AcquisitionImmunity** campaign parameter)
and then broadcasts an event based on the results; positive has immunity while negative does not.
Note that **Base_Sensitivity** and **Base_Specificity** function whether or not the immunity is
above the threshold.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-immunitybloodtest.csv") }}

```json
{
    "Events":[{
            "class":"CampaignEvent",
            "Start_Day":14,
            "Nodeset_Config":{
                "class":"NodeSetAll"
            },
            "Event_Coordinator_Config":{
                "class":"StandardInterventionDistributionEventCoordinator",
                "Target_Demographic":"Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "Base_Sensitivity": 1.0,
                    "Base_Specificity": 1.0,
                    "Cost_To_Consumer": 0,
                    "Days_To_Diagnosis": 0.0,
                    "Positive_Diagnosis_Event": "TestedPositive_IamImmune",
                    "Negative_Diagnosis_Event": "TestedNegative_IamSusceptible",
                    "Treatment_Fraction": 1.0,
                    "Positive_Threshold_AcquisitionImmunity": 0.99,
                    "class": "ImmunityBloodTest"
                }
            }
        }],
    "Use_Defaults":1
}
```
