# StandardInterventionDistributionEventCoordinator


The **StandardInterventionDistributionEventCoordinator** coordinator class distributes an individual-level or
node-level intervention to a specified fraction of individuals or nodes within a node set. Recurring
campaigns can be created by specifying the number of times distributions should occur and the time
between repetitions. 

Demographic restrictions such as **Demographic_Coverage** and **Target_Gender** do not apply when
distributing node-level interventions. The node-level intervention must handle the demographic
restrictions.

See the following JSON example and table, which shows all available parameters
for this event coordinator.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-standardinterventiondistributioneventcoordinator.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "Event_Name": "Outbreak",
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 1,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Demographic_Coverage": 0.005,
            "Intervention_Config": {
                "Outbreak_Source": "PrevalenceIncrease",
                "class": "OutbreakIndividual"
            }
        }
    }]
}
```
