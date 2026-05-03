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
