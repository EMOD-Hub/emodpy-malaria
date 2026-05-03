# FirstNodeWithNodePropertyEventCoordinator


The **FirstNodeWithNodePropertyEventCoordinator** coordinator class screens for
a desired node property (NP) and then broadcasts a coordinator event when found. When this 
event coordinator is triggered to start, it goes through the provided list of nodes and checks 
the NPs of each. (The nodes in the provided list must be defined in the CampaignEvent's **Nodeset_Config** 
parameter.) Once a node is found with the desired NP, the coordinator event is broadcast. An additional 
coordinator event can be broadcast if the desired NP is NOT found.


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-firstnodewithnodepropertyeventcoordinator.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 50,
        "Event_Coordinator_Config": {
            "class": "FirstNodeWithNodePropertyEventCoordinator",
            "Start_Trigger_Condition_List": [ "Send_People_To_Node" ],
            "Node_Property_Key_Value_To_Have" : "Place:URBAN",
            "Node_ID_To_Coordinator_Event_List": [
                { "Node_ID":  2, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_2" },
                { "Node_ID":  3, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_3" },
                { "Node_ID":  4, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_4" },
                { "Node_ID":  5, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_5" },
                { "Node_ID":  6, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_6" },
                { "Node_ID":  7, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_7" },
                { "Node_ID":  8, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_8" },
                { "Node_ID":  9, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_9" },
                { "Node_ID": 10, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_10" },
                { "Node_ID": 11, "Coordinator_Event_To_Broadcast": "Send_People_To_Node_11" }
            ],
            "Not_Found_Coordinator_Event": "My_Not_Found_Event"
        }
    }]
}
```
