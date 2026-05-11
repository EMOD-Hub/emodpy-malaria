# ArtificialDiet


The **ArtificialDiet** intervention class is used to include feeding stations for vectors within a
node in a simulation. This is a node-targeted intervention and takes effect at the broad village
level rather than at the individual level. For individual-level effects, use
[HumanHostSeekingTrap](parameter-campaign-individual-humanhostseekingtrap.md) instead. An artificial diet
diverts some of the vectors seeking to blood feed that day, resulting in a two-fold benefit:

1. The uninfected mosquitoes avoid biting infected humans some of the time, therefore
   decreasing the amount of human-to-vector transmission.

1. Infectious vectors are diverted to feed on the artificial diet instead of the humans, therefore
   decreasing the amount of vector-to-human transmission.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** No
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** No killing
*  **Vector effects:** Artificial Diet Feed instead of Human or Animal Feed
*  **Vector sexes affected:** Meal-seeking females only.
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

{{ read_csv("csv/campaign-artificialdiet.csv", keep_default_na=False) }}

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
                "Intervention_Config": {
                    "class": "ArtificialDiet",
                    "Artificial_Diet_Target": "AD_WithinVillage",
                    "Attraction_Config": {
                        "Initial_Effect": 0.5,
                        "Box_Duration": 100,
                        "Decay_Time_Constant": 150,
                        "class": "WaningEffectBoxExponential"
                    },
                    "Cost_To_Consumer": 10.0
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
