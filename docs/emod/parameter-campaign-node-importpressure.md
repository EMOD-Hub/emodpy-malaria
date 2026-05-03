# ImportPressure


The **ImportPressure** intervention class extends **Outbreak** by importing infected individuals
into a node at a configurable rate over specified time periods. Each element in the
**Daily_Import_Pressures** array is applied for the corresponding number of days in the
**Durations** array, allowing time-varying importation schedules. The imported cases are
created with the specified **Antigen**, **Genome**, and **Import_Age**.

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
