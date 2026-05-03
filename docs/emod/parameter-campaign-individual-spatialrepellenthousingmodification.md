# SpatialRepellentHousingModification


The **SpatialRepellentHousingModification** intervention class is a housing modification utilizing
spatial repellents. The protection provided by this intervention is exclusively against
indoor-biting mosquitoes.

At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, when it has been distributed to individuals.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific vectors.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** No. Already existing intervention(s) continues to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** No killing.
*  **Vector effects:** Repelling.
*  **Vector sexes affected:** Indoor meal-seeking females only
*  **Vector life stage affected:** Adult

{% include "../reuse/warning-housing-mods.txt" %}

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-spatialrepellenthousingmodification.csv") }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 120,
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.8,
                "Intervention_Config": {
                    "class": "SpatialRepellentHousingModification",
                    "Cost_To_Consumer": 1.0,
                    "Repelling_Config": {
                        "Box_Duration": 100,
                        "Decay_Time_Constant": 150,
                        "Initial_Effect": 0.1,
                        "class": "WaningEffectBoxExponential"
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
