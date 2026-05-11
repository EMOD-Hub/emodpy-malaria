# IndividualImmunityChanger


The **IndividualImmunityChanger** intervention class acts essentially as a
[MultiEffectVaccine](parameter-campaign-individual-multieffectvaccine.md),
with the exception of how the behavior is implemented. Rather than
attaching a persistent vaccine intervention object to an individual’s intervention list (as a
campaign-individual-multieffectboostervaccine does), the **IndividualImmunityChanger** directly
alters the immune modifiers of the individual’s susceptibility object and is then immediately disposed
of. Any immune waning is not governed by [Waning effects](parameter-campaign-waningeffects.md), as
[MultiEffectVaccine](parameter-campaign-individual-multieffectvaccine.md) is, but rather
by the immunity waning parameters in the configuration file.

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

{{ read_csv("csv/campaign-individualimmunitychanger.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "Generic Seattle Regression Campaign",
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 10,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "IndividualImmunityChanger",
                    "Cost_To_Consumer": 10.0,
                    "Prime_Acquire": 0.1,
                    "Prime_Transmit": 0.2,
                    "Prime_Mortality": 0.3,
                    "Boost_Acquire": 0.7,
                    "Boost_Transmit": 0.7,
                    "Boost_Mortality": 1.0,
                    "Boost_Threshold_Acquire": 0.2,
                    "Boost_Threshold_Transmit": 0.1,
                    "Boost_Threshold_Mortality": 0.1
                }
            }
        }
    ]
}
```
