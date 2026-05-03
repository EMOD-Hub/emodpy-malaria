# SpatialRepellentHousingModification


The **SpatialRepellentHousingModification** intervention class is a housing modification utilizing
spatial repellents. The protection provided by this intervention is exclusively against
indoor-biting mosquitoes.

At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, when it has been distributed to individuals.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific vectors.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** No. Already existing intervention(s) continues to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** No killing.
*  **Vector effects:** Repelling.
*  **Vector sexes affected:** Indoor meal-seeking females only
*  **Vector life stage affected:** Adult

.. warning::

    |EMOD_s| simulations models nodes and individuals within nodes; they do not
    model houses. Therefore, housing modifications are received by individuals, not houses.

    Use of this class and other housing modification classes requires caution because they can have 
    unintended effects. For example, individuals in the same household may receive different housing
    modification interventions.  An individual receiving a housing modification intervention who
    then migrates to another node will continue to receive that intervention. We recommend that you 
    configure your simulation to take these logical inconsistencies into account. 

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

{{ read_csv("csv/campaign-spatialrepellenthousingmodification.csv") }}

```json
{
    "Events": [
        {
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
                    "class": "SpatialRepellentHousingModification",
                    "Cost_To_Consumer": 1.0,
                    "Repelling_Config": {
                        "Box_Duration": 100,
                        "Decay_Time_Constant": 150,
                        "Initial_Effect": 0.1,
                        "class": "WaningEffectBoxExponential"
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
