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


!!! warning
    EMOD simulations models nodes and individuals within nodes; they do not
    model houses. Therefore, housing modifications are received by individuals, not houses.

    Use of this class and other housing modification classes requires caution because they can have 
    unintended effects. For example, individuals in the same household may receive different housing
    modification interventions.  An individual receiving a housing modification intervention who
    then migrates to another node will continue to receive that intervention. We recommend that you 
    configure your simulation to take these logical inconsistencies into account. 
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
