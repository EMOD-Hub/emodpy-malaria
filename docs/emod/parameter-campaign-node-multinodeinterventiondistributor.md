# MultiNodeInterventionDistributor


The **MultiNodeInterventionDistributor** intervention class is a node-level intervention that
distributes multiple other node-level  interventions when the distributor only allows specifying one
intervention. This class can be thought of as an "adapter," where it can adapt interventions or
coordinators that were designed to distribute one intervention to instead distribute many.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-multinodeinterventiondistributor.csv") }}

```json
{
    "Intervention_Config": {
        "class": "MultiNodeInterventionDistributor",
        "Node_Intervention_List": [
            {
                "class": "SpaceSpraying",
                "Cost_To_Consumer": 1.0, 
                "Habitat_Target": "ALL_HABITATS", 
                "Spray_Kill_Target": "SpaceSpray_Indoor",
                "Killing_Config": {
                    "class": "WaningEffectExponential",
                    "Initial_Effect": 1.0,
                    "Decay_Time_Constant": 90
                        }, 
                "Reduction_Config": {
                    "class": "WaningEffectExponential",
                    "Initial_Effect": 1.0,
                    "Decay_Time_Constant": 90
                        }
            }, 
            {
                "class": "NodePropertyValueChanger",
                "Target_NP_Key_Value": "InterventionStatus:RECENT_SPRAY", 
                "Daily_Probability": 1.0, 
                "Maximum_Duration": 0, 
                "Revert": 90
            }
        ]
    }
}
```
