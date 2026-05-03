# VectorSurveillanceEventCoordinator


The **VectorSurveillanceEventCoordinator** coordinator class samples the vector population
at regular intervals and reports allele frequencies or genome fractions. It is configured with
a **Counter** object that specifies the species, gender, sample size, and counting method, and
a **Responder** object that can broadcast an event each time a survey is completed. Sampling
is controlled by trigger events: the coordinator begins sampling when an event from
**Start_Trigger_Condition_List** is received, and stops when an event from
**Stop_Trigger_Condition_List** is received or the **Duration** expires.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-vectorsurveillanceeventcoordinator.csv") }}

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
            "class": "VectorSurveillanceEventCoordinator",
            "Coordinator_Name": "Allele_Frequency_Monitor",
            "Duration": -1,
            "Start_Trigger_Condition_List": [
                "Start_Vector_Surveillance"
            ],
            "Stop_Trigger_Condition_List": [],
            "Counter": {
                "Count_Type": "ALLELE_FREQ",
                "Species": "gambiae",
                "Gender": "VECTOR_FEMALE",
                "Sample_Size_Distribution": "CONSTANT_DISTRIBUTION",
                "Sample_Size_Constant": 100,
                "Update_Period": 30
            },
            "Responder": {
                "Survey_Completed_Event": "Vector_Survey_Done"
            }
        }
    }]
}
```
