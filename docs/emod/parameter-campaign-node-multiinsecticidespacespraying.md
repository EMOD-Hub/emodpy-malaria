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
