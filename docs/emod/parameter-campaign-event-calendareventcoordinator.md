# CalendarEventCoordinator


The **CalendarEventCoordinator** coordinator class distributes individual-level interventions at a specified
time and coverage. See the following JSON example and table, which shows all available parameters
for this event coordinator.

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

{{ read_csv("csv/campaign-calendareventcoordinator.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Event_Name": "High-risk vaccination",
        "Start_Day": 1,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "CalendarEventCoordinator",
            "Demographic_Coverage": 1,
            "Property_Restrictions": [
                "Risk:High"
            ],
            "Number_Repetitions": 1,
            "Timesteps_Between_Repetitions": 0,
            "Target_Demographic": "Everyone",
            "Target_Residents_Only": 1,
            "Distribution_Times": [100, 200, 400, 800, 1200],
            "Distribution_Coverages": [0.01, 0.05, 0.1, 0.2, 1.0],
            "Intervention_Config": {
                "Cost_To_Consumer": 0,
                "Vaccine_Take": 1,
                "Vaccine_Type": "AcquisitionBlocking",
                "class": "SimpleVaccine",
                "Waning_Config": {
                    "Initial_Effect": 1,
                    "Box_Duration": 1825,
                    "class": "WaningEffectBox"
                }
            }
        }
    }]
}
```
