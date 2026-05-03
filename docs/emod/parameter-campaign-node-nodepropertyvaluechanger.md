# NodePropertyValueChanger


The **NodePropertyValueChanger** intervention class sets a given node property to a new value. You can
also define a duration in days before the node property reverts back to its original value, the
probability that a node will change its node property to the target value, and the number of days
over which nodes will attempt to change their individual properties to the target value. This
node-level intervention functions in a similar manner as the individual-level intervention,
[parameter-campaign-individual-propertyvaluechanger](parameter-campaign-individual-propertyvaluechanger.md).

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-nodepropertyvaluechanger.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 40,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Node_Property_Restrictions": [{
                "InterventionStatus": "VACCINATING"
            }],
            "Intervention_Config": {
                "class": "NodePropertyValueChanger",
                "Target_NP_Key_Value": "InterventionStatus:STOP_VACCINATING",
                "Daily_Probability": 1.0,
                "Maximum_Duration": 0,
                "Revert": 0
            }
        }
    }]
}
```
