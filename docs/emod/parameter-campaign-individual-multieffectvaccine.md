# MultiEffectVaccine


The **MultiEffectVaccine** intervention class implements vaccine campaigns in the simulation.
Vaccines can effect all of the following:

* Reduce the likelihood of acquiring an infection
* Reduce the likelihood of transmitting an infection
* Reduce the likelihood of death

After distribution, the effect wanes over time.

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

{{ read_csv("csv/campaign-multieffectvaccine.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "ExplicitAgeRanges",
                "Target_Age_Min": 12,
                "Target_Age_Max": 100,
                "Demographic_Coverage": 1,
                "Property_Restrictions": ["Accessibility:VaccineTake"],
                "Intervention_Config": {
                    "class": "MultiEffectVaccine",
                    "Cost_To_Consumer": 20,
                    "Vaccine_Take": 1,
                    "Vaccine_Type": "Generic",
                    "Acquire_Config": {
                        "class": "WaningEffectExponential",
                        "Initial_Effect": 0.9,
                        "Decay_Time_Constant": 7300
                    },
                    "Transmit_Config": {
                        "class": "WaningEffectExponential",
                        "Initial_Effect": 0.9,
                        "Decay_Time_Constant": 7300
                    },
                    "Mortality_Config": {
                        "class": "WaningEffectExponential",
                        "Initial_Effect": 1.0,
                        "Decay_Time_Constant": 7300
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
