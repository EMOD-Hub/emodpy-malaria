# MigrateFamily


The **MigrateFamily** intervention class tells family groups of residents of the targeted node to go
on a round trip migration ("family trip"). The duration of time residents wait before migration and
the time spent at the destination node can be configured; the pre-migration waiting timer does not
start until all residents are at the *home node*.

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

{{ read_csv("csv/campaign-migratefamily.csv") }}

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
        "class": "StandardInterventionDistributionEventCoordinator",
        "Intervention_Config": {
          "class": "NodeLevelHealthTriggeredIV",
          "Trigger_Condition_List": [
            "NewInfectionEvent"
          ],
          "Demographic_Coverage": 1.0,
          "Actual_NodeIntervention_Config": {
            "class": "MigrateFamily",
            "NodeID_To_Migrate_To": 4,
            "Duration_Before_Leaving_Distribution": "CONSTANT_DISTRIBUTION",
            "Duration_At_Node_Distribution": "CONSTANT_DISTRIBUTION",
            "Is_Moving": 0,
            "Duration_Before_Leaving_Constant": 0,
            "Duration_At_Node_Constant": 10
          }
        }
      }
    }
  ]
}
```
