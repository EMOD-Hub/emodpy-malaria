# MultiInsecticideSpaceSpraying


The **MultiInsecticideSpaceSpraying** intervention class is a node-level intervention that models
the application of a multi-insecticide outdoor spray. As a spray, this kills male and female adult
and immature mosquitoes. Mosquitoes have a daily probability of dying; feeding status does not impact
the probability of death for adult female mosquitoes.

The effectiveness of the intervention is combined using the following equation:

Total efficacy = 1.0 – (1.0 – efficacy_1)* (1.0 – efficacy_2) * … * (1.0 – efficacy_n)


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes, especially when targeting certain species.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Without Attempting to Feed & Die Before Attempting Human Feed
*  **Vector effects:** Killing
*  **Vector sexes affected:** Both males and females
*  **Vector life stage affected:** Adult and immature

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-multiinsecticidespacespraying.csv") }}

```json
{
    "Events": [{
        "Event_Coordinator_Config": {
            "Intervention_Config": {
                "class": "MultiInsecticideSpaceSpraying",
                "Cost_To_Consumer": 1.0,
                "Spray_Coverage": 1.0,
                "Insecticides": [{
                        "Insecticide_Name": "pyrethroid_homo",
                        "Killing_Config": {
                            "Box_Duration": 100,
                            "Decay_Time_Constant": 150,
                            "Initial_Effect": 0.1,
                            "class": "WaningEffectBoxExponential"
                        }
                    },
                    {
                        "Insecticide_Name": "carbamate_homo",
                        "Killing_Config": {
                            "Box_Duration": 100,
                            "Decay_Time_Constant": 150,
                            "Initial_Effect": 0.1,
                            "class": "WaningEffectBoxExponential"
                        }
                    }
                ]
            },
            "class": "StandardInterventionDistributionEventCoordinator"
        },
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 100,
        "class": "CampaignEvent"
    }],
    "Use_Defaults": 1
}
```
