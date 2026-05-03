# AnimalFeedKill


The **AnimalFeedKill** intervention class imposes node-targeted mortality to a vector that
feeds on animals.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes, can be used to target sub-groups using genomes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Before Attempting to Feed
*  **Vector effects:** Killing
*  **Vector sexes affected:** Females seeking non-human blood meals only.
*  **Vector life stage affected:** Adult


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-animalfeedkill.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 120,
        "Nodeset_Config": {
            "class": "NodeSetAlld"
        },
        "Event_Coordinator_Config": {
            "class": "NodeEventCoordinator",
            "Intervention_Config": {
                "class": "AnimalFeedKill",
                "Cost_To_Consumer": 10.0,
                "Killing_Config": {
                    "Box_Duration": 100,
                    "Decay_Time_Constant": 150,
                    "Initial_Effect": 0.2,
                    "class": "WaningEffectBoxExponential"
                }
            }
        }
    }],
    "Use_Defaults": 1
}
```
