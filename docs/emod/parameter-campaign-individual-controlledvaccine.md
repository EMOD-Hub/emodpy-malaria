# ControlledVaccine


The **ControlledVaccine** intervention class is a subclass of [parameter-campaign-individual-simplevaccine](parameter-campaign-individual-simplevaccine.md)
so it contains all functionality of **SimpleVaccine**, but provides more control over
additional events and event triggers. This intervention can be configured so that specific events
are broadcast when individuals receive an intervention or when the intervention expires. Further,
individuals can be re-vaccinated, using a configurable wait time between vaccinations.

Note that one of the controls of this intervention is to not allow a person to receive an additional
dose if they received a dose within a certain amount of time. This applies only to **ControlledVaccine**
interventions with the same **Intervention_Name**, so people can be given multiple vaccines as long
as each vaccine has a different value for **Intervention_Name**.


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-controlledvaccine.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
            "COMMENT": "Vaccinate Everyone with VaccineA",
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
                            "Times": [0, 25, 50],
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
            "COMMENT": "After the first round expires, distribute a different vaccine, VaccineB",
            "class": "CampaignEvent",
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
                            "Times": [0, 25, 50],
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
