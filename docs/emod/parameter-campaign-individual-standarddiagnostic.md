# StandardDiagnostic


The **StandardDiagnostic** intervention class identifies infected individuals, regardless of disease
state, based on specified diagnostic sensitivity and specificity. Diagnostics are a key component of 
modern disease control efforts, whether used to identify high-risk individuals, infected individuals, 
or drug resistance. The individual receives the diagnostic test immediately when the intervention is
distributed, but there may be a delay in receiving a positive result. This intervention class
distributes a specified intervention to a fraction of individuals who test positive.

This class is similar to [parameter-campaign-individual-simplediagnostic](parameter-campaign-individual-simplediagnostic.md), but allows the user to
specify an action upon receipt of a negative diagnosis.




{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-standarddiagnostic.csv") }}

```json
{
    "Events":[{
            "class":"CampaignEvent",
            "Start_Day":200,
            "Nodeset_Config":{
                "class":"NodeSetAll"
            },
            "Event_Coordinator_Config":{
                "class":"StandardInterventionDistributionEventCoordinator",
                "Target_Demographic":"Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config":{
                    "class":"SimpleDiagnostic",
                    "Base_Sensitivity":1.0,
                    "Base_Specificity":1.0,
                    "Cost_To_Consumer":0,
                    "Days_To_Diagnosis":5.0,
                    "Dont_Allow_Duplicates":0,
                    "Event_Or_Config":"Event",
                    "Positive_Diagnosis_Event":"Acorn",
                    "Intervention_Name":"Diagnostic_Sample",
                    "Treatment_Fraction":1.0
                }
            }
        }],
    "Use_Defaults":1
}
```
