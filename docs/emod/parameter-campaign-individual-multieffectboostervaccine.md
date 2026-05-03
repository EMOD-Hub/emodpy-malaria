# MultiEffectBoosterVaccine


The **MultiEffectBoosterVaccine** intervention class is derived from
[parameter-campaign-individual-multieffectvaccine](parameter-campaign-individual-multieffectvaccine.md) and preserves many of the same parameters.
Upon distribution and successful take, the vaccine’s effect in each immunity compartment
(acquisition, transmission,  and mortality) is determined by the recipient’s immune state. If the
recipient’s immunity modifier in the corresponding compartment is above a user-specified threshold,
then the vaccine’s initial effect will be equal to the corresponding priming parameter. If the
recipient’s immune modifier is below this threshold, then the vaccine’s initial effect will be equal
to the corresponding boost parameter. After distribution, the effect wanes, just like a
**MultiEffectVaccine**. The behavior is intended to mimic biological priming and boosting.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-multieffectboostervaccine.csv") }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "Generic Seattle Regression Campaign",
    "Events": [{
        "Event_Coordinator_Config": {
            "Demographic_Coverage": 1.0,
            "Intervention_Config": {
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
                    "Box_Duration": 100,
                    "Initial_Effect": 0.5,
                    "class": "WaningEffectBox"
                },
                "Transmit_Config": {
                    "Box_Duration": 100,
                    "Initial_Effect": 0.5,
                    "class": "WaningEffectBox"
                },
                "Mortality_Config": {
                    "Box_Duration": 100,
                    "Initial_Effect": 0.5,
                    "class": "WaningEffectBox"
                },
                "class": "MultiEffectBoosterVaccine"
            },
            "Target_Demographic": "Everyone",
            "class": "StandardInterventionDistributionEventCoordinator"
        },
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 1,
        "class": "CampaignEvent"
    }]
}
```
