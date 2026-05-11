# MosquitoRelease


The **MosquitoRelease** intervention class adds mosquito release vector control programs to the simulation.
Mosquito release is a key vector control mechanism that allows the release of sterile males,
genetically modified mosquitoes, or even Wolbachia- or Microsporidia-infected mosquitoes.
See [Vector control configuration](parameter-configuration-vector-control.md) configuration parameters for more information.

Released vectors are added to the population and participate in the vector life cycle and mating system the same day.

You can also release already-mated females to guarantee specific genomes in the offspring by setting the **Released_Mate_Genome** parameter.

See [Vector genetics](vector-model-genetics.md) for information on defining vector genomes, gene drivers, and insecticide resistance alleles. See [Microsporidia](vector-model-microsporidia.md) for information on microsporidia strains and their transmission dynamics within vector populations.
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

{{ read_csv("csv/campaign-mosquitorelease.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Event_Name": "MosquitoRelease",
            "Start_Day": 5,
            "Nodeset_Config": {"class": "NodeSetAll"},
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "MosquitoRelease",
                    "Cost_To_Consumer": 200,
                    "Released_Type": "Ratio",
                    "Released_Ratio": 1.5,
                    "Released_Infectious": 0.5,
                    "Released_Species": "SillySkeeter",
                    "Released_Wolbachia": "VECTOR_WOLBACHIA_FREE",
                    "Released_Genome": [["X", "Y"], ["a1", "a1"]]
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Event_Name": "MosquitoRelease",
            "Start_Day": 125,
            "Nodeset_Config": {"class": "NodeSetAll"},
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "MosquitoRelease",
                    "Cost_To_Consumer": 200,
                    "Released_Type": "FIXED_NUMBER",
                    "Released_Number": 35000,
                    "Released_Species": "SillySkeeter",
                    "Released_Wolbachia": "VECTOR_WOLBACHIA_A",
                    "Released_Genome": [["X", "X"], ["b0", "b0"]]
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Event_Name": "MosquitoRelease_Microsporidia",
            "Start_Day": 200,
            "Nodeset_Config": {"class": "NodeSetAll"},
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "MosquitoRelease",
                    "Cost_To_Consumer": 200,
                    "Released_Type": "FIXED_NUMBER",
                    "Released_Number": 50000,
                    "Released_Species": "gambiae",
                    "Released_Microsporidia_Strain": "Strain_A",
                    "Released_Genome": [["X", "X"], ["a1", "a1"]]
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Event_Name": "MosquitoRelease Pre-mated",
            "Start_Day": 200,
            "Nodeset_Config": {"class": "NodeSetAll"},
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "MosquitoRelease",
                    "Cost_To_Consumer": 300,
                    "Released_Type": "FIXED_NUMBER",
                    "Released_Number": 20000,
                    "Released_Species": "SillySkeeter",
                    "Released_Genome": [["X", "X"], ["a1", "a1"]],
                    "Released_Mate_Genome": [["X", "Y"], ["a1", "a1"]]
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
