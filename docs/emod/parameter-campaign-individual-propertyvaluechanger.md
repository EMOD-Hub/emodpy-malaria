# PropertyValueChanger


The **PropertyValueChanger** intervention class assigns new individual property values to
individuals. You must update one property value and have the option to update another using
**New_Property_Value**. This parameter is generally used to move patients from one intervention
state in the health care cascade (InterventionStatus) to another, though it can be used for any
individual property. Individual property values are user-defined in the demographics file (see
[demo-properties](#demo-properties) for more information). Note that the HINT feature
does not need to be enabled to use this intervention. To instead change node properties, use
[parameter-campaign-node-nodepropertyvaluechanger](parameter-campaign-node-nodepropertyvaluechanger.md).

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-propertyvaluechanger.csv") }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 10,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1.0,
                "Property_Restrictions": [
                    "Risk:LOW"
                ],
                "Intervention_Config": {
                    "class": "PropertyValueChanger",
                    "Disqualifying_Properties": [ "InterventionStatus:Diagnosed"],
                    "New_Property_Value": "InterventionStatus:Monitor",
                    "Target_Property_Key" : "Risk",
                    "Target_Property_Value" : "HIGH",
                    "Daily_Probability" : 1.0,
                    "Maximum_Duration" : 0,
                    "Revert" : 10
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
