# SimpleVaccine


The **SimpleVaccine** intervention class implements vaccine campaigns in the simulation. Vaccines can have
an effect on one of the following:

* Reduce the likelihood of acquiring an infection
* Reduce the likelihood of transmitting an infection
* Reduce the likelihood of death

To configure vaccines that have an effect on more than one of these, use
[MultiEffectVaccine](parameter-campaign-individual-multieffectvaccine.md) instead.

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

{{ read_csv("csv/campaign-simplevaccine.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 60,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
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
                        "class": "WaningEffectBox",
                        "Box_Duration": 3650,
                        "Initial_Effect": 1
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
