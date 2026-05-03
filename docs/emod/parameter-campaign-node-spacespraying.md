# SpaceSpraying


The **SpaceSpraying** intervention class implements node-level vector control by spraying pesticides
outdoors. This intervention targets specific habitat types, and imposes a mortality rate on all
targeted (both immature and adult male and female) mosquitoes. All mosquitoes have daily mortality
rates; mortality for adult females due to spraying is independent of whether or not they are
feeding.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No. You need to redistribute when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes, especially if you want to target specific sexes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Without Attempting To Feed & Die Before Attempting Human Feed
*  **Vector effects:** Killing
*  **Vector sexes affected:** Males and females
*  **Vector life stage affected:** Adult and immature



{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-spacespraying.csv") }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "SpaceSpraying",
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 4,
        "Event_Coordinator_Config": {
            "class": "NodeEventCoordinator",
            "Intervention_Config": {
                "class": "SpaceSpraying",
                "Cost_To_Consumer": 0,
                "Killing_Config": {
                    "class": "WaningEffectBoxExponential",
                    "Box_Duration": 100,
                    "Decay_Time_Constant": 150,
                    "Initial_Effect": 1
                },
                "Insecticide_Name": "carbamate",
                "Spray_Coverage": 0.9
            }
        }
    }]
}
```
