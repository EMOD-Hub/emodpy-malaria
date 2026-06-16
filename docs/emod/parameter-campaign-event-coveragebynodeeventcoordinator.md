# CoverageByNodeEventCoordinator


The **CoverageByNodeEventCoordinator** distributes individual-level interventions with
node-specific demographic coverage. It is similar to the
[StandardInterventionDistributionEventCoordinator](parameter-campaign-event-standardeventcoordinator.md)
but adds the ability to specify different coverage fractions for each node via the
**Coverage_By_Node** parameter. Each entry in **Coverage_By_Node** is a pair of node ID and
coverage value. If no coverage has been specified for a particular node ID, the coverage
defaults to zero for that node.

This coordinator supports the same demographic targeting, property restrictions, repetition, and
targeting config options as the standard event coordinator.

!!! note
    This can only be used with individual-level interventions, but EMOD will not produce an error
    if you attempt to use it with a node-level intervention.

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

{{ read_csv("csv/campaign-coveragebynodeeventcoordinator.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [1, 2, 3]
            },
            "Event_Coordinator_Config": {
                "class": "CoverageByNodeEventCoordinator",
                "Target_Demographic": "Everyone",
                "Number_Repetitions": 1,
                "Coverage_By_Node": [
                    {
                        "Node_Id": 1,
                        "Coverage": 0.6
                    },
                    {
                        "Node_Id": 2,
                        "Coverage": 0.9
                    },
                    {
                        "Node_Id": 3,
                        "Coverage": 0.1
                    }
                ],
                "Intervention_Config": {
                    "class": "SimpleVaccine",
                    "Vaccine_Type": "AcquisitionBlocking",
                    "Vaccine_Take": 1,
                    "Waning_Config": {
                        "class": "WaningEffectBox",
                        "Initial_Effect": 1,
                        "Box_Duration": 3650
                    }
                }
            }
        }
    ]
}
```
