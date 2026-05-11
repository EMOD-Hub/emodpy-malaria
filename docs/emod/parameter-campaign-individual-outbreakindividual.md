# OutbreakIndividual


The **OutbreakIndividual** intervention class introduces contagious diseases that are compatible
with the simulation type to existing individuals using the individual targeted features configured
in the appropriate event coordinator. To instead add new infection individuals, use [Outbreak](parameter-campaign-node-outbreak.md).

Note, when using **Malaria_Model**: MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS, do not use
this intervention class. Instead, use [OutbreakIndividualMalariaGenetics](parameter-campaign-individual-outbreakindividualmalariagenetics.md).

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

{{ read_csv("csv/campaign-outbreakindividual.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 30,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.001,
                "Intervention_Config": {
                    "class": "OutbreakIndividual",
                    "IgnoreImmunity": 1,
                    "Antigen": 0,
                    "Genome": 0
                }
            }
        }
    ]
}
```
