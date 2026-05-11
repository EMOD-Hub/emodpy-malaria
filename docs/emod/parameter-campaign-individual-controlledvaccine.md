# ControlledVaccine


The **ControlledVaccine** intervention class is a subclass of [SimpleVaccine](parameter-campaign-individual-simplevaccine.md)
so it contains all functionality of **SimpleVaccine**, but provides more control over
additional events and event triggers. This intervention can be configured so that specific events
are broadcast when individuals receive an intervention or when the intervention expires. Further,
individuals can be re-vaccinated, using a configurable wait time between vaccinations.

Note that one of the controls of this intervention is to not allow a person to receive an additional
dose if they received a dose within a certain amount of time. This applies only to **ControlledVaccine**
interventions with the same **Intervention_Name**, so people can be given multiple vaccines as long
as each vaccine has a different value for **Intervention_Name**.


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

{{ read_csv("csv/campaign-controlledvaccine.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "COMMENT": "Vaccinate Everyone with VaccineA",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "ControlledVaccine",
                    "Intervention_Name": "VaccineA",
                    "Cost_To_Consumer": 1,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Vaccine_Take": 1.0,
                    "Waning_Config": {
                        "class": "WaningEffectMapLinear",
                        "Initial_Effect": 1.0,
                        "Expire_At_Durability_Map_End": 1,
                        "Durability_Map": {
                            "Times":  [0,   25,  50],
                            "Values": [1.0, 1.0, 0.0]
                        }
                    },
                    "Distributed_Event_Trigger": "VaccinatedA",
                    "Expired_Event_Trigger": "VaccineExpiredA",
                    "Duration_To_Wait_Before_Revaccination": 40
                }
            }
        },
        {
            "class": "CampaignEvent",
            "COMMENT": "After the first round expires, distribute a different vaccine, VaccineB",
            "Start_Day": 60,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "ControlledVaccine",
                    "Intervention_Name": "VaccineB",
                    "Cost_To_Consumer": 1,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Vaccine_Take": 1.0,
                    "Waning_Config": {
                        "class": "WaningEffectMapLinear",
                        "Initial_Effect": 1.0,
                        "Expire_At_Durability_Map_End": 1,
                        "Durability_Map": {
                            "Times":  [0,   25,  50],
                            "Values": [1.0, 1.0, 0.0]
                        }
                    },
                    "Distributed_Event_Trigger": "VaccinatedB",
                    "Expired_Event_Trigger": "VaccineExpiredB",
                    "Duration_To_Wait_Before_Revaccination": 40
                }
            }
        }
    ]
}
```
