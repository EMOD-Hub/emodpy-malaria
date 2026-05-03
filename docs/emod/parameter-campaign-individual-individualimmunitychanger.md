# IndividualImmunityChanger


The **IndividualImmunityChanger** intervention class acts essentially as a
[parameter-campaign-individual-multieffectvaccine](parameter-campaign-individual-multieffectvaccine.md),
with the exception of how the behavior is implemented. Rather than
attaching a persistent vaccine intervention object to an individual’s intervention list (as a
campaign-individual-multieffectboostervaccine does), the **IndividualImmunityChanger** directly
alters the immune modifiers of the individual’s susceptibility object and is then immediately disposed
of. Any immune waning is not governed by [parameter-campaign-waningeffects](parameter-campaign-waningeffects.md), as
[parameter-campaign-individual-multieffectvaccine](parameter-campaign-individual-multieffectvaccine.md) is, but rather
by the immunity waning parameters in the configuration file.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-individualimmunitychanger.csv") }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "Generic Seattle Regression Campaign",
    "Events": [{
        "Start_Day": 10,
        "class": "CampaignEvent",
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
    }]
}
```
