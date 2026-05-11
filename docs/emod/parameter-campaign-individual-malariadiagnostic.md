# MalariaDiagnostic



The **MalariaDiagnostic** intervention class is similar to 
[SimpleDiagnostic](parameter-campaign-individual-simplediagnostic.md), but distributes a test
for malaria. There are several types of configurable diagnostic tests, and the
type selected determines the other parameters used. 

You should note that the results of **MalariaDiagnostic** can be different
than what you see in the reports.  The intervention takes an independent
measurement from the reports.  It has its own parameters that control the
sensitivity and detection threshold.


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

{{ read_csv("csv/campaign-malariadiagnostic.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 18050,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.5,
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition": "TriggerString",
                    "Trigger_Condition_String": "Diagnostic_Survey_2",
                    "Actual_IndividualIntervention_Config": {
                        "class": "MalariaDiagnostic",
                        "Cost_To_Consumer": 0,
                        "Diagnostic_Type": "BLOOD_SMEAR_PARASITES",
                        "Measurement_Sensitivity": 0.1,
                        "Detection_Threshold": 3,
                        "Event_Or_Config": "Config",
                        "Positive_Diagnosis_Config": {
                            "class": "AntimalarialDrug",
                            "Cost_To_Consumer": 5,
                            "Drug_Type": "Chloroquine"
                        },
                        "Negative_Diagnosis_Config": {
                            "class": "SimpleVaccine",
                            "Cost_To_Consumer": 10,
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
            }
        }
    ],
    "Use_Defaults": 1
}
```
