# MultiEffectBoosterVaccine


The **MultiEffectBoosterVaccine** intervention class is derived from
[MultiEffectVaccine](parameter-campaign-individual-multieffectvaccine.md) and preserves many of the same parameters.
Upon distribution and successful take, the vaccine’s effect in each immunity compartment
(acquisition, transmission,  and mortality) is determined by the recipient’s immune state. If the
recipient’s immunity modifier in the corresponding compartment is above a user-specified threshold,
then the vaccine’s initial effect will be equal to the corresponding priming parameter. If the
recipient’s immune modifier is below this threshold, then the vaccine’s initial effect will be equal
to the corresponding boost parameter. After distribution, the effect wanes, just like a
**MultiEffectVaccine**. The behavior is intended to mimic biological priming and boosting.

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

{{ read_csv("csv/campaign-multieffectboostervaccine.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "Generic Seattle Regression Campaign",
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "MultiEffectBoosterVaccine",
                    "Cost_To_Consumer": 10.0,
                    "Vaccine_Take": 1,
                    "Prime_Acquire": 0.1,
                    "Prime_Transmit": 0.2,
                    "Prime_Mortality": 0.3,
                    "Boost_Acquire": 0.7,
                    "Boost_Transmit": 0.5,
                    "Boost_Mortality": 1.0,
                    "Boost_Threshold_Acquire": 0.0,
                    "Boost_Threshold_Transmit": 0.0,
                    "Boost_Threshold_Mortality": 0.0,
                    "Acquire_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 100,
                        "Initial_Effect": 0.5
                    },
                    "Transmit_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 100,
                        "Initial_Effect": 0.5
                    },
                    "Mortality_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 100,
                        "Initial_Effect": 0.5
                    }
                }
            }
        }
    ]
}
```
