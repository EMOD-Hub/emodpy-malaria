# MultiNodeInterventionDistributor


The **MultiNodeInterventionDistributor** intervention class is a node-level intervention that
distributes multiple other node-level  interventions when the distributor only allows specifying one
intervention. This class can be thought of as an "adapter," where it can adapt interventions or
coordinators that were designed to distribute one intervention to instead distribute many.

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
