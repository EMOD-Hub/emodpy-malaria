# IndoorIndividualEmanator


The **IndoorIndividualEmanator** intervention class is a house modification intervention and it imitates the use of
personal mosquito repellents that are designed for indoor use, such as mosquito coils or vaporizer mats. These
interventions release insecticides into the air to repel or kill mosquitoes in the vicinity of the
individual using the emanator. The intervention is distributed to individuals, allowing for
targeting specific subgroups of the population.

The intervention acts on female vectors seeking a blood meal indoors. Once the vectors is indoors, it is first
repelled based on the repelling effect. Then, the vectors that are not repelled, are subjected to the
killing effect. Vectors that are not repelled or killed can proceed to try to bite the individual and will
be subject to other individual indoor interventions. After the vectors have successfully fed (human or non-human meal),
the are subjected again to the killing effect of the emanator before exiting the indoor environment. Hence,
the IndoorIndividualEmanator can contribute to both Indoor Die Before Feeding and Indoor Die After Feeding.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** No. Already existing intervention(s) continues to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die Before Feeding, Indoor Die After Feeding
*  **Vector effects:** Repelling and killing
*  **Vector sexes affected:** Females seeking blood meal indoors only
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

{{ read_csv("csv/campaign-indoorindividualemanator.csv") }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 540,
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.8,
                "Intervention_Config": {
                    "class": "IndoorIndividualEmanator",
                    "Repelling_Config": {
                        "Box_Duration": 3650,
                        "Initial_Effect": 0,
                        "class": "WaningEffectBox"
                    },
                    "Cost_To_Consumer": 8,
                    "Killing_Config": {
                        "Box_Duration": 3650,
                        "Initial_Effect": 0.5,
                        "class": "WaningEffectBox"
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
