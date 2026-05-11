# IRSHousingModification


The **IRSHousingModification** intervention class includes Indoor Residual Spraying (IRS) in the
simulation. IRS is another key vector control tool in which insecticide is sprayed on the interior
walls of a house so that mosquitoes resting on the walls after consuming a blood meal will die. IRS
can also have a repellent effect. Because this class is distributed to individuals, it can target
subgroups of the population. To target all individuals in a node, use
[IndoorSpaceSpraying](parameter-campaign-node-indoorspacespraying.md). Do not use **IRSHousingModification** and
**IndoorSpaceSpraying** together.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** No. Already existing intervention(s) of this class continue(s) to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die After Feeding
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

{{ read_csv("csv/campaign-irshousingmodification.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 540,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.8,
                "Intervention_Config": {
                    "class": "IRSHousingModification",
                    "Cost_To_Consumer": 8,
                    "Repelling_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 3650,
                        "Initial_Effect": 0
                    },
                    "Killing_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 3650,
                        "Initial_Effect": 0.5
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
