# ScreeningHousingModification


The **ScreeningHousingModification** intervention class implements housing screens as a vector
control effort. Housing screens are used to decrease the number of mosquitoes that can enter indoors
and therefore reduce indoor biting.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Indoor After Feeding, Die Indoor Before Feeding
*  **Vector effects:** Repelling and killing
*  **Vector sexes affected:** Indoor meal-seeking females only
*  **Vector life stage affected:** Adult


{% include "../reuse/warning-housing-mods.txt" %}

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-screeninghousingmodification.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 120,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 0.8,
            "Intervention_Config": {
                "class": "ScreeningHousingModification",
                "Repelling_Config": {
                    "Box_Duration": 100,
                    "Decay_Time_Constant": 150,
                    "Initial_Effect": 0.8,
                    "class": "WaningEffectBoxExponential"
                },
                "Cost_To_Consumer": 1.0,
                "Killing_Config": {
                    "Box_Duration": 100,
                    "Decay_Time_Constant": 150,
                    "Initial_Effect": 0.0,
                    "class": "WaningEffectBoxExponential"
                }
            }
        }
    }],
    "Use_Defaults": 1
}
```
