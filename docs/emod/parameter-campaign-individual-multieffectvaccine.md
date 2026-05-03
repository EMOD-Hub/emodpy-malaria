# MultiEffectVaccine


The **MultiEffectVaccine** intervention class implements vaccine campaigns in the simulation.
Vaccines can effect all of the following:

* Reduce the likelihood of acquiring an infection
* Reduce the likelihood of transmitting an infection
* Reduce the likelihood of death

After distribution, the effect wanes over time.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-multieffectvaccine.csv") }}

```json
{
    "Events": [{
        "Event_Coordinator_Config": {
            "Demographic_Coverage": 1,
            "Intervention_Config": {
                "Cost_To_Consumer": 20,
                "Vaccine_Take": 1,
                "Vaccine_Type": "Generic",
                "class": "MultiEffectVaccine",
                "Acquire_Config": {
                    "Initial_Effect": 0.9,
                    "Decay_Time_Constant": 7300,
                    "class": "WaningEffectExponential"
                },
                "Transmit_Config": {
                    "Initial_Effect": 0.9,
                    "Decay_Time_Constant": 7300,
                    "class": "WaningEffectExponential"
                },
                "Mortality_Config": {
                    "Initial_Effect": 1.0,
                    "Decay_Time_Constant": 7300,
                    "class": "WaningEffectExponential"
                }
            },
            "Property_Restrictions": [
                "Accessibility:VaccineTake"
            ],
            "Target_Age_Max": 100,
            "Target_Age_Min": 12,
            "Target_Demographic": "ExplicitAgeRanges",
            "class": "StandardInterventionDistributionEventCoordinator"
        },
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 1,
        "class": "CampaignEvent"
    }],
    "Use_Defaults": 1
}
```
