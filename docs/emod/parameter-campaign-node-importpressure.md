# ImportPressure


The **ImportPressure** intervention class extends **Outbreak** by importing infected individuals
into a node at a configurable rate over specified time periods. Each element in the
**Daily_Import_Pressures** array is applied for the corresponding number of days in the
**Durations** array, allowing time-varying importation schedules. The imported cases are
created with the specified **Antigen**, **Genome**, and **Import_Age**.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-importpressure.csv") }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "Initial Seeding",
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 1,
        "Event_Name": "Outbreak",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 1.0,
            "Intervention_Config": {
                "Antigen": 0,
                "Genome": 0,
                "Durations": [100, 100, 100, 100, 100, 100, 100],
                "Daily_Import_Pressures": [0.1, 5.0, 0.2, 1.0, 2.0, 0.0, 10.0],
                "class": "ImportPressure"
            }
        }
    }]
}
```
