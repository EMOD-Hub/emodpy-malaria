# SugarTrap


The **SugarTrap** intervention class implements a vector sugar-baited trap to collect/kill
sugar-feeding mosquitoes and is sometimes called an attractive toxic sugar bait (ATSB). This
intervention affects all mosquitoes living and feeding at a given node. Male vectors sugar-feed
daily and female vectors sugar-feed once per blood meal (or upon emergence), so these traps can
impact male survival on a daily basis. Efficacy can be modified using per-sex insecticide
resistance.

The impact of sugar-baited traps will depend on the sugar-feeding behavior specified in the
configuration file via **Vector_Sugar_Feeding_Frequency**, whether there is no sugar feeding, sugar
feeding occurs once at emergence, sugar feeding occurs once per blood meal, or sugar feeding occurs
every day. Note that if it is set to VECTOR_SUGAR_FEEDING_NONE, this intervention will have no
effect. See [Vector control configuration](parameter-configuration-vector-control.md) configuration parameters for more
information.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No. It will need to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes or specific sexes.
*  **Time-based expiration:** Yes. Expiration time can be specified using specific distributions.
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Sugar Trap Killing
*  **Vector effects:** Killing
*  **Vector sexes affected:** Males and females
*  **Vector life stage affected:** Adult and immature when they are emerging (if configured)


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

{{ read_csv("csv/campaign-sugartrap.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Nodeset_Config": {"class": "NodeSetAll"},
            "Start_Day": 1460,
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Intervention_Config": {
                    "class": "SugarTrap",
                    "Cost_To_Consumer": 3.75,
                    "Killing_Config": {
                        "class": "WaningEffectExponential",
                        "Decay_Time_Constant": 2190,
                        "Initial_Effect": 0.1
                    },
                    "Expiration_Distribution": "CONSTANT_DISTRIBUTION",
                    "Expiration_Constant": 360
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
