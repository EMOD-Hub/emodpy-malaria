# SimpleIndividualRepellent


The **SimpleIndividualRepellent** intervention class provides protection to individuals against both
indoor-feeding and outdoor-feeding mosquito bites.

At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, when it has been distributed to individuals.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific vectors.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** No killing
*  **Vector effects:** Repelling.
*  **Vector sexes affected:** All meal-seeking females
*  **Vector life stage affected:** Adult

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

{{ read_csv("csv/campaign-simpleindividualrepellent.csv") }}

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
            "Demographic_Coverage": 0.5,
            "Intervention_Config": {
                "class": "SimpleIndividualRepellent",
                "Repelling_Config": {
                    "Box_Duration": 100,
                    "Decay_Time_Constant": 150,
                    "Initial_Effect": 0.8,
                    "class": "WaningEffectBoxExponential"
                },
                "Cost_To_Consumer": 10.0
            }
        }
    }],
    "Use_Defaults": 1
}
```
