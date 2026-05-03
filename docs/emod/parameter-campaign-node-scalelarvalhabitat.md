# ScaleLarvalHabitat


The **ScaleLarvalHabitat** intervention class is a node-level intervention that enables
species-specific habitat modification within shared habitat types. This intervention has a similar
function to the demographic parameter **ScaleLarvalMultiplier**, but enables habitat availability to
be modified at any time or at any location during the simulation, as specified in the campaign
event.

To reset the multiplier, you must either replace the existing one with a new intervention with the same
Intervention_Name where the multiplier/factor is 1.0 or use the **Disqualifying_Properties** to cause the
intervention to abort.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** No
*  **Time-based expiration:** No. It will continue to exist even if the efficacy is zero.
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Does not apply
*  **Vector effects:** Does not apply
*  **Vector sexes affected:** both
*  **Vector life stage affected:** eggs and larva, depending on oviposition settings

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

{{ read_csv("csv/campaign-scalelarvalhabitat.csv") }}

```json
{
  "Use_Defaults": 1,
  "Events": [
    {
      "class": "CampaignEvent",
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Start_Day": 730,
      "Event_Coordinator_Config": {
        "Intervention_Config": {
          "Larval_Habitat_Multiplier": {
            "LarvalHabitatMultiplier": [
              {
                "Factor": 0.05,
                "Habitat": "CONSTANT",
                "Species": "Gambiae"
              },
              {
                "Factor": 0.05,
                "Habitat": "TEMPORARY_RAINFALL",
                "Species": "ALL_SPECIES"
              }
            ]
          },
          "class": "ScaleLarvalHabitat"
        },
        "class": "StandardInterventionDistributionEventCoordinator"
      }
    }
  ]
}
```
