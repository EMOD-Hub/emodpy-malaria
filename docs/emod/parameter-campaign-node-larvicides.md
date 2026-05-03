# Larvicides


The **Larvicides** intervention class is a node-level intervention that configures a killing effect for larva
in specific habitats. This intervention can be used to simulate the application of larvicides to water bodies.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific genders.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** No. Already existing intervention(s) of this class continue(s) to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Combines with competition and rainfall to kill larvae every time step.
*  **Vector effects:** Killing
*  **Vector sexes affected:** Both males and female larva
*  **Vector life stage affected:** Larval

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-larvicides.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 140,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "Cost_To_Consumer": 3.75,
                "Spray_Coverage": 0.6,
                "Habitat_Target": "ALL_HABITATS",
                "Larval_Killing_Config": {
                    "Box_Duration": 3650,
                    "Initial_Effect": 0.1,
                    "class": "WaningEffectBox"
                },
                "class": "Larvicides"
            }
        }
    }],
    "Use_Defaults": 1
}
```
