# OutbreakIndividual


The **OutbreakIndividual** intervention class introduces contagious diseases that are compatible
with the simulation type to existing individuals using the individual targeted features configured
in the appropriate event coordinator. To instead add new infection individuals, use [parameter-campaign-node-outbreak](parameter-campaign-node-outbreak.md).

Note, when using **Malaria_Model**: MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS, do not use
this intervention class. Instead, use [parameter-campaign-individual-outbreakindividualmalariagenetics](parameter-campaign-individual-outbreakindividualmalariagenetics.md).

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-outbreakindividual.csv") }}

```json
{
  "Events": [
    {
      "Event_Coordinator_Config": {
        "Demographic_Coverage": 0.001,
        "Intervention_Config": {
          "Clade": 1,
          "Genome": 3,
          "IgnoreImmunity": 1,
          "class": "OutbreakIndividual"
        },
        "Target_Demographic": "Everyone",
        "class": "StandardInterventionDistributionEventCoordinator"
      },
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Start_Day": 30,
      "class": "CampaignEvent"
    }
  ]
}
```
