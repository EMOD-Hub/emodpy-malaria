# MigrateFamily


The **MigrateFamily** intervention class tells family groups of residents of the targeted node to go
on a round trip migration ("family trip"). The duration of time residents wait before migration and
the time spent at the destination node can be configured; the pre-migration waiting timer does not
start until all residents are at the *home node*.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

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
