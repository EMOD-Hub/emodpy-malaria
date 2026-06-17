# IncidenceEventCoordinator


The **IncidenceEventCoordinator** monitors for individual-level events within a simulation and
responds by broadcasting events when configurable thresholds are met. It does not distribute
interventions directly; instead, it counts specified events using an **Incidence_Counter** and
evaluates the accumulated count or percentage against thresholds defined in a **Responder**. The
responder then broadcasts the appropriate event, which can trigger other campaign events or event
coordinators.

The coordinator operates in a count-respond cycle:

1. The **Incidence_Counter** listens for individual events specified in **Trigger_Condition_List**
   and counts them over a configurable number of timesteps (**Count_Events_For_Num_Timesteps**).
   Only events from individuals matching the demographic and property restrictions are counted.
2. When the counting period ends, the **Responder** calculates the incidence value as a raw count
   or percentage (based on **Threshold_Type**).
3. The responder selects the action from **Action_List** whose **Threshold** is the highest value
   that is still less than or equal to the calculated incidence.
4. The selected action's **Event_To_Broadcast** event is broadcast as an individual, node, or
   coordinator event (based on **Event_Type**).
5. If configured with repetitions, the cycle repeats after **Timesteps_Between_Repetitions**.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.

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

{{ read_csv("csv/campaign-incidenceeventcoordinator.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "IncidenceEventCoordinator",
                "Coordinator_Name": "MDA_Trigger",
                "Number_Repetitions": -1,
                "Timesteps_Between_Repetitions": 30,
                "Incidence_Counter": {
                    "Count_Events_For_Num_Timesteps": 7,
                    "Demographic_Coverage": 1.0,
                    "Target_Demographic": "Everyone",
                    "Trigger_Condition_List": [
                        "NewClinicalCase"
                    ]
                },
                "Responder": {
                    "Threshold_Type": "COUNT",
                    "Action_List": [
                        {
                            "Threshold": 0,
                            "Event_To_Broadcast": "NoResponse",
                            "Event_Type": "COORDINATOR"
                        },
                        {
                            "Threshold": 50,
                            "Event_To_Broadcast": "MDA_Campaign_Start",
                            "Event_Type": "COORDINATOR"
                        }
                    ]
                }
            }
        }
    ]
}
```
