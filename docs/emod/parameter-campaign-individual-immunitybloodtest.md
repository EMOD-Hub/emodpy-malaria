# ImmunityBloodTest


The **ImmunityBloodTest** intervention class identifies whether an individual's immunity meets a
specified threshold (as set with the **Positive_Threshold_AcquisitionImmunity** campaign parameter)
and then broadcasts an event based on the results; positive has immunity while negative does not.
Note that **Base_Sensitivity** and **Base_Specificity** function whether or not the immunity is
above the threshold.

.. note::

    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    |EMOD_s| does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with |EMOD_s| will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not |EMOD_s| parameter names will be ignored by the
    model.

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv("csv/campaign-immunitybloodtest.csv") }}

```json
{
    "Events":[{
            "class":"CampaignEvent",
            "Start_Day":14,
            "Nodeset_Config":{
                "class":"NodeSetAll"
            },
            "Event_Coordinator_Config":{
                "class":"StandardInterventionDistributionEventCoordinator",
                "Target_Demographic":"Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "Base_Sensitivity": 1.0,
                    "Base_Specificity": 1.0,
                    "Cost_To_Consumer": 0,
                    "Days_To_Diagnosis": 0.0,
                    "Positive_Diagnosis_Event": "TestedPositive_IamImmune",
                    "Negative_Diagnosis_Event": "TestedNegative_IamSusceptible",
                    "Treatment_Fraction": 1.0,
                    "Positive_Threshold_AcquisitionImmunity": 0.99,
                    "class": "ImmunityBloodTest"
                }
            }
        }],
    "Use_Defaults":1
}
```
