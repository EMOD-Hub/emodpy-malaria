# FemaleContraceptive


The **FemaleContraceptive** intervention class models contraceptive use among women.
It is an individual-level intervention that reduces fertility for a configurable duration
with a configurable waning efficacy. The **Usage_Duration_Distribution** determines how long
each woman uses the contraceptive, and the **Waning_Config** controls how the efficacy
changes over that period. When a woman stops using the contraceptive, the
**Usage_Expiration_Event** is broadcast.

This intervention applies only when **Birth_Rate_Dependence** in config.json is set to "INDIVIDUAL_PREGNANCIES" or "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR".

At a glance:

*  **Distributed to:** Individuals (females only)
*  **Serialized:** Yes. It will be preserved when starting from a serialized file.
*  **Time-based expiration:** Yes. It expires when the usage duration expires, which is determined by the **Usage_Duration_Distribution**.
*  **Purge existing:** No. Adding a new intervention of this class will not remove any existing interventions and efficacies will combine as `birth_modifier *= new_birth_modifier`.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-femalecontraceptive.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 1,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "NodeLevelHealthTriggeredIV",
                "Trigger_Condition_List": ["NewClinicalCase"],
                "Demographic_Coverage": 0.5,
                "Target_Gender": "Female",
                "Actual_IndividualIntervention_Config": {
                    "class": "FemaleContraceptive",
                    "Cost_To_Consumer": 5,
                    "Usage_Duration_Distribution": "CONSTANT_DISTRIBUTION",
                    "Usage_Duration_Constant": 180,
                    "Usage_Expiration_Event": "ContraceptiveExpired",
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 180,
                        "Initial_Effect": 0.95
                    }
                }
            }
        }
    }]
}
```
