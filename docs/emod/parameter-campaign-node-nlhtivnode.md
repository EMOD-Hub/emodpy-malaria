# NLHTIVNode


The **NLHTIVNode** intervention class distributes node-level interventions to nodes when a specific
user-defined node event occurs. For example, **NLHTIVNode** can be configured to have
**SurveillanceEventCoordinator** set to listen for **NewInfectionEvents**, and then broadcast a
node event when a certain number of events is reached, such as distributing **IndoorSpaceSpraying**
to a node with a high number of new infections.

**NLHTIVNode** is similar to [NodeLevelHealthTriggeredIV](parameter-campaign-node-nodelevelhealthtriggerediv.md) but **NLHTIVNode**
is focused on *node* interventions and events while **NodeLevelHealthTriggeredIV** is focused on
*individual* interventions and events.

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

{{ read_csv("csv/campaign-nlhtivnode.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "comment": "No infections, Negative_Event_Node",
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "NLHTIVNode",
                    "Trigger_Condition_List": ["SheddingComplete"],
                    "Duration": 1000,
                    "Blackout_Event_Trigger": "Blackout",
                    "Blackout_Period": 100.0,
                    "Blackout_On_First_Occurrence": 0,
                    "Actual_NodeIntervention_Config": {
                        "class": "EnvironmentalDiagnostic",
                        "Sample_Threshold": 0.0,
                        "Environment_IP_Key_Value": "Risk:High",
                        "Base_Specificity": 1.0,
                        "Base_Sensitivity": 1.0,
                        "Negative_Diagnostic_Event": "Negative_Event_Node",
                        "Positive_Diagnostic_Event": "Positive_Event_Node"
                    }
                }
            }
        }
    ]
}
```
