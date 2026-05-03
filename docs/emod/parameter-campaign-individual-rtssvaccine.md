# RTSSVaccine


The **RTSSVaccine** intervention class protects individuals against infection acquisition by
directly boosting the *circumsporozoite protein (CSP)* antibody concentration. This contrasts
with the [parameter-campaign-individual-simplevaccine](parameter-campaign-individual-simplevaccine.md) intervention, which is used to modify
the probability of acquisition or transmission.

The CSP antibody reduces the probability that sporozoites survive to infect the liver/hepatocytes. A
higher **Boosted_Antibody_Concentration** means the person will be less likely to have sporozoites
survive and infect the hepatocytes. Without the vaccine, CSP does not do anything. The following
[parameter-configuration-immunity](parameter-configuration-immunity.md) parameters impact CSP and its sporozoite killing ability:

*  **Antibody_CSP_Killing_Threshold**
*  **Antibody_CSP_Killing_Inverse_Width**
*  **Antibody_CSP_Decay_Days**

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-rtssvaccine.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 20,
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
    }],
    "Use_Defaults": 1
}
```
