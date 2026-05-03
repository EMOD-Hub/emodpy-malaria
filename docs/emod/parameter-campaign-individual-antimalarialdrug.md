# AntimalarialDrug


The **AntimalarialDrug** intervention is used to apply drug-based control efforts to malaria
simulations. When configuring this intervention, note that the configuration parameter
**Malaria_Drug_Params** must be configured, as it governs how particular anti-malarial drugs will
behave.


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-antimalarialdrug.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
         "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 270,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 0.8,
            "Intervention_Config": {
                "class": "AntimalarialDrug",
                "Cost_To_Consumer": 3.75,
                "Dont_Allow_Duplicates": 1,
                "Drug_Type": "Chloroquine"
            },
            "Number_Repetitions": 1,
            "Timesteps_Between_Repetitions": 0
        }
    }]
}
```
