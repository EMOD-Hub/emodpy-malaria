# BirthTriggeredIV


Note: This intervention has been replaced by NodeLevelHealthTriggeredIV, which provides more flexibility and can be
triggered by any individual event, including **Births** which mimics the BirthTriggeredIV. BirthTriggeredIV will
continue to be supported for backward compatibility but will not receive new features.

The **BirthTriggeredIV** intervention class listens for births in a node and distributes
an individual-level intervention to each newborn. It is a node-level intervention that persists
on the node for the specified **Duration** (or indefinitely if set to -1), distributing the
configured **Actual_IndividualIntervention_Config** to qualifying newborns based on demographic
targeting and property restrictions.

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

{{ read_csv("csv/campaign-birthtriggerediv.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 1,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "BirthTriggeredIV",
                "Duration": -1,
                "Demographic_Coverage": 0.95,
                "Target_Demographic": "Everyone",
                "Actual_IndividualIntervention_Config": {
                    "class": "SimpleVaccine",
                    "Cost_To_Consumer": 10,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Waning_Config": {
                        "class": "WaningEffectExponential",
                        "Decay_Time_Constant": 365,
                        "Initial_Effect": 0.8
                    }
                }
            }
        }
    }]
}
```
