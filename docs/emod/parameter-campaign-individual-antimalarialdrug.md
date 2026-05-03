# AntimalarialDrug


The **AntimalarialDrug** intervention is used to apply drug-based control efforts to malaria
simulations. When configuring this intervention, note that the configuration parameter
**Malaria_Drug_Params** must be configured, as it governs how particular anti-malarial drugs will
behave.


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
