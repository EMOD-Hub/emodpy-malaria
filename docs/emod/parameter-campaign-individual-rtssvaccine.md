# RTSSVaccine


The **RTSSVaccine** intervention class protects individuals against infection acquisition by
directly boosting the *circumsporozoite protein (CSP)* antibody concentration. This contrasts
with the [SimpleVaccine](parameter-campaign-individual-simplevaccine.md) intervention, which is used to modify
the probability of acquisition or transmission.

The CSP antibody reduces the probability that sporozoites survive to infect the liver/hepatocytes. A
higher **Boosted_Antibody_Concentration** means the person will be less likely to have sporozoites
survive and infect the hepatocytes. Without the vaccine, CSP does not do anything. The following
[Immunity configuration](parameter-configuration-immunity.md) parameters impact CSP and its sporozoite killing ability:

*  **Antibody_CSP_Killing_Threshold**
*  **Antibody_CSP_Killing_Inverse_Width**
*  **Antibody_CSP_Decay_Days**

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

{{ read_csv("csv/campaign-rtssvaccine.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 20,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 0.8,
                "Intervention_Config": {
                    "class": "RTSSVaccine",
                    "Boosted_Antibody_Concentration": 1200,
                    "Cost_To_Consumer": 1.0
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
