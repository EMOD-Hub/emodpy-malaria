# SimpleHealthSeekingBehavior


The **SimpleHealthSeekingBehavior** intervention class models the time delay that typically occurs
between when an individual experiences onset of symptoms and when they seek help from a health care
provider. Several factors may contribute to such delays including accessibility, cost, and trust in
the health care system. This intervention models this time delay as an exponential process; at every
time step, the model draws randomly to determine if the individual will receive the specified
intervention. As an example, this intervention can be nested in a **NodeLevelHealthTriggeredIV** so
that when an individual is infected, he or she receives a **SimpleHealthSeekingBehavior**,
representing that the individual will now seek care. The individual subsequently seeks care with an
exponentially distributed delay and ultimately receives the specified intervention.

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

{{ read_csv("csv/campaign-simplehealthseekingbehavior.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Event_Name": "Testing after new infection",
            "Start_Day": 9125,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Number_Repetitions": 1,
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1,
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": ["NewInfectionEvent"],
                    "Actual_IndividualIntervention_Config": {
                        "class": "SimpleHealthSeekingBehavior",
                        "Event_Or_Config": "Config",
                        "Tendency": 0.0015,
                        "Actual_IndividualIntervention_Config": {
                            "class": "SimpleDiagnostic",
                            "Base_Sensitivity": 0.9,
                            "Base_Specificity": 0.8,
                            "Event_Or_Config": "Event",
                            "Positive_Diagnosis_Event": "TestedPositive"
                        }
                    }
                }
            }
        }
    ]
}
```
