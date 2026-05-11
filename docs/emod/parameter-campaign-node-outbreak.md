# Outbreak


The **Outbreak** class allows the introduction of a disease outbreak event by the addition of new
infected or susceptible individuals to a node. **Outbreak** is a node-level
intervention; to distribute an outbreak to specific categories of existing individuals within a
node, use [OutbreakIndividual](parameter-campaign-individual-outbreakindividual.md).

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

{{ read_csv("csv/campaign-outbreak.csv", keep_default_na=False) }}

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
            "Nodeset_Config": {"class": "NodeSetAll"},
            "Start_Day": 30,
            "class": "CampaignEvent"
        }
    ]
}
```
