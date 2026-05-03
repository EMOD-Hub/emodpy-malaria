# MalariaChallenge


The **MalariaChallenge** intervention class is a node-level intervention similar to
[parameter-campaign-node-outbreak](parameter-campaign-node-outbreak.md). However, instead of distributing infections, it distributes
malaria challenges by either tracking numbers of sporozoites or infectious mosquito bites.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-malariachallenge.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 40,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "MalariaChallenge",
                "Challenge_Type": "InfectiousBites",
                "Coverage": 1.0,
                "Infectious_Bite_Count": 2,
                "Sporozoite_Count": 3
            }
        }
    }]
}
```
