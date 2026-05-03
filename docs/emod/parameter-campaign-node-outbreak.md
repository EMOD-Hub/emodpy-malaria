# Outbreak


The **Outbreak** class allows the introduction of a disease outbreak event by the addition of new
infected or susceptible individuals to a node. **Outbreak** is a node-level
intervention; to distribute an outbreak to specific categories of existing individuals within a
node, use [parameter-campaign-individual-outbreakindividual](parameter-campaign-individual-outbreakindividual.md).

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-outbreak.csv") }}

```json
{
  "Events": [
    {
      "Event_Coordinator_Config": {
        "Demographic_Coverage": 0.001,
        "Intervention_Config": {
          "Clade": 1,
          "Genome": 3,
          "Import_Age": 365,
          "Number_Cases_Per_Node": 10,
          "Probability_Of_Infection": 0.7,
          "class": "Outbreak"
        },
        "Target_Demographic": "Everyone",
        "class": "StandardInterventionDistributionEventCoordinator"
      },
      "Event_Name": "Outbreak",
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Start_Day": 30,
      "class": "CampaignEvent"
    }
  ]
}
```
