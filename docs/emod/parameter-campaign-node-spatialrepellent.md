# SpatialRepellent


The **SpatialRepellent** intervention class implements node-level spatial repellents exclusively against
vectors looking to feed that day.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** No killing but Survive Without Successful Feed
*  **Vector effects:** Repelling
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult



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

{{ read_csv("csv/campaign-spatialrepellent.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 120,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "SpatialRepellent",
                "Repelling_Config": {
                    "Box_Duration": 100,
                    "Decay_Time_Constant": 150,
                    "Initial_Effect": 0.4,
                    "class": "WaningEffectBoxExponential"
                },
                "Cost_To_Consumer": 1.0,
                "Spray_Coverage": 0.6
            }
        }
    }],
    "Use_Defaults": 1
}
```
