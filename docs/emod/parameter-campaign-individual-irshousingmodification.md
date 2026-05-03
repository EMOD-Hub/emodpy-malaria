# IRSHousingModification


The **IRSHousingModification** intervention class includes Indoor Residual Spraying (IRS) in the
simulation. IRS is another key vector control tool in which insecticide is sprayed on the interior
walls of a house so that mosquitoes resting on the walls after consuming a blood meal will die. IRS
can also have a repellent effect. Because this class is distributed to individuals, it can target
subgroups of the population. To target all individuals in a node, use
[parameter-campaign-node-indoorspacespraying](parameter-campaign-node-indoorspacespraying.md). Do not use **IRSHousingModification** and
**IndoorSpaceSpraying** together.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** No. Already existing intervention(s) of this class continue(s) to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die After Feeding
*  **Vector effects:** Repelling and killing
*  **Vector sexes affected:** Indoor meal-seeking females only
*  **Vector life stage affected:** Adult



{% include "../reuse/warning-housing-mods.txt" %}

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-irshousingmodification.csv") }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 540,
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.8,
                "Intervention_Config": {
                    "class": "IRSHousingModification",
                    "Repelling_Config": {
                        "Box_Duration": 3650,
                        "Initial_Effect": 0,
                        "class": "WaningEffectBox"
                    },
                    "Cost_To_Consumer": 8,
                    "Killing_Config": {
                        "Box_Duration": 3650,
                        "Initial_Effect": 0.5,
                        "class": "WaningEffectBox"
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
