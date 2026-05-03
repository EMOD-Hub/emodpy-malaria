# IVCalendar


The **IVCalendar** intervention class contains a list of ages when an individual will receive the
actual intervention. In **IVCalendar**, there is a list of actual interventions where the
distribution is dependent on whether the individual's age matches the next date in the calendar.
This implies that at a certain age, the list of actual interventions will be distributed according
to a given probability. While a typical use case might involve the distribution of calendars by a
[parameter-campaign-node-birthtriggerediv](parameter-campaign-node-birthtriggerediv.md) in the context of a routine vaccination schedule, calendars
may also be distributed directly to individuals.

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

{{ read_csv("csv/campaign-ivcalendar.csv") }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "BCG vaccination calendar distributed at birth",
    "Events": [{
        "Event_Name": "BCG vaccinations scheduled at birth",
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 1825,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Intervention_Config": {
                "class": "BirthTriggeredIV",
                "Demographic_Coverage": 0.9,
                "Actual_IndividualIntervention_Config": {
                    "class": "IVCalendar",
                    "Calendar": [{
                            "Age": 30,
                            "Probability": 1
                        },
                        {
                            "Age": 3650,
                            "Probability": 1
                        }
                    ],
                    "Dropout": 0,
                    "Actual_IndividualIntervention_Configs": [{
                        "class": "BCGVaccine",
                        "Cost_To_Consumer": 8,
                        "Vaccine_Take": 0.8,
                        "Vaccine_Take_Age_Decay_Rate": 0.2,
                        "Waning_Config": {
                            "Initial_Rate": 0.9,
                            "Decay_Time_Constant": 3650,
                            "class": "WaningEffectExponential"
                        }
                    }]
                }
            }
        }
    }]
}
```
