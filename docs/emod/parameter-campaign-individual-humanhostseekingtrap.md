# HumanHostSeekingTrap


The **HumanHostSeekingTrap** intervention class applies a trap that attracts and kills indoor host-seeking
mosquitoes in the simulation. Human-host-seeking traps are individually-distributed interventions
that have attraction and killing rates that decay in an analogous fashion to the blocking and
killing rates of bednets.

An artificial diet diverts the vector from feeding on the human population, resulting in a two-fold
benefit:

1. The uninfected mosquitoes avoid biting infected humans some of the time, therefore decreasing the amount of human-to-vector transmission.
1. Infectious vectors are diverted to feed on artificial diet instead of humans, therefore decreasing the amount of vector-to-human transmission.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** No
*  **Time-based expiration:** No
*  **Purge existing:** Yes. Adding a new intervention of this class will replace an existing intervention of the same class in an individual. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Indoor Die Before Feeding
*  **Vector effects:** Artificial Diet feed instead of Human or Animal Feed
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

{{ read_csv("csv/campaign-humanhostseekingtrap.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 140,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 0.7,
            "Intervention_Config": {
                "class": "HumanHostSeekingTrap",
                "Cost_To_Consumer": 3.75,
                "Attract_Config": {
                    "Box_Duration": 3650,
                    "Initial_Effect": 0.6,
                    "class": "WaningEffectBox"
                },
                "Killing_Config": {
                    "Box_Duration": 3650,
                    "Initial_Effect": 0.9,
                    "class": "WaningEffectBox"
                }
            }
        }
    }],
    "Use_Defaults": 1
}
```
