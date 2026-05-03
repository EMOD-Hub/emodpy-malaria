# SimpleVaccine


The **SimpleVaccine** intervention class implements vaccine campaigns in the simulation. Vaccines can have
an effect on one of the following:

* Reduce the likelihood of acquiring an infection
* Reduce the likelihood of transmitting an infection
* Reduce the likelihood of death

To configure vaccines that have an effect on more than one of these, use
[parameter-campaign-individual-multieffectvaccine](parameter-campaign-individual-multieffectvaccine.md) instead.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-simplevaccine.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 60,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 0.5,
            "Intervention_Config": {
                "class": "SimpleVaccine",
                "Cost_To_Consumer": 10.0,
                "Vaccine_Take": 1,
                "Vaccine_Type": "AcquisitionBlocking",
                "Waning_Config": {
                    "Box_Duration": 3650,
                    "Initial_Effect": 1,
                    "class": "WaningEffectBox"
                }
            }
        }
    }],
    "Use_Defaults": 1
}
```
