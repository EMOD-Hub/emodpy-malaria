# Ivermectin


The **Ivermectin** intervention class modifies the feeding outcome probabilities for both indoor-
and outdoor-feeding mosquitoes. Ivermectin works by increasing the mortality of mosquitoes after they
blood-feed on a human. It is an individually-distributed intervention that configures the waning of
the drug's killing effect on the adult mosquito population. This intervention enables exploration of
the impact of giving humans an insecticidal drug, and how the effectiveness and duration of the
drug's killing-effect interacts with other interventions. For example, you can look at the impact of
controlling and eliminating malaria transmission using both anti-parasite drugs that clear existing
infections and insecticidal drugs.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No, but it will expire if the efficacy is below 0.00001.
*  **Purge existing:** No. Already existing intervention(s) of this class continue(s) to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor/Outdoor Die After Feeding
*  **Vector effects:** Killing
*  **Vector sexes affected:** Meal-seeking females only
*  **Vector life stage affected:** Adult


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-ivermectin.csv") }}

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
                "Number_Repetitions": 5,
                "Target_Demographic": "Everyone",
                "Timesteps_Between_Repetitions": 3,
                "Demographic_Coverage": 0.8,
                "Intervention_Config": {
                    "class": "Ivermectin",
                    "Cost_To_Consumer": 1,
                    "Killing_Config": {
                        "Box_Duration": 3,
                        "Initial_Effect": 1,
                        "class": "WaningEffectBox"
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
