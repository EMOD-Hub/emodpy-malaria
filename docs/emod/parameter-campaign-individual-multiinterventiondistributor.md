# MultiInterventionDistributor


The **MultiInterventionDistributor** intervention class allows you to input a list of
interventions, rather than just a single intervention, to be distributed simultaneously to the same
individuals.

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

{{ read_csv("csv/campaign-multiinterventiondistributor.csv") }}

```json
{
    "Events": [{
        "class": "SimpleDiagnostic",
        "Treatment_Fraction": 0.7,
        "Base_Sensitivity": 0.8,
        "Base_Specificity": 0.9,
        "Cost_To_Consumer": 0,
        "Days_To_Diagnosis": 0.0,
        "Event_Or_Config": "Config",
        "Positive_Diagnosis_Config": {
            "class": "MultiInterventionDistributor",
            "Intervention_List": [{
                    "class": "SimpleVaccine",
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Vaccine_Take": 1,
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 3650,
                        "Initial_Effect": 0.1
                    }
                },
                {
                    "class": "SimpleVaccine",
                    "Vaccine_Type": "TransmissionBlocking",
                    "Vaccine_Take": 1,
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 3650,
                        "Initial_Effect": 0.9
                    }
                },
                {
                    "class": "SimpleVaccine",
                    "Vaccine_Type": "MortalityBlocking",
                    "Vaccine_Take": 1,
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 3650,
                        "Initial_Effect": 0.5
                    }
                }
            ]
        }
    }]
}
```
