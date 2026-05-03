# IndividualNonDiseaseDeathRateModifier


The **IndividualNonDiseaseDeathRateModifier** intervention class provides a method of modifying 
an individual's non-disease mortality rate over time, until an expiration event is reached. For example, 
this intervention could be given to people who have access to health care to model that 
they have a different life expectancy than those who do not. Different distribution patterns 
can be designated, and linear interpolation will be used to calculate values between time points.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-individualnondiseasedeathratemodifier.csv") }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 3000,
            "Nodeset_Config": { "class": "NodeSetAll" },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "IndividualNonDiseaseDeathRateModifier",
                    "Cost_To_Consumer": 1,
                    "Duration_To_Modifier" : {
                        "Times" : [ 0.0, 365.0, 730.0, 1095.0 ],
                        "Values": [ 2.0,   1.0,   0.5,    0.0 ]
                    },
                    "Expiration_Duration_Distribution": "CONSTANT_DISTRIBUTION",
                    "Expiration_Duration_Constant": 1000,
                    "Expiration_Event": "BackToNormalMortality"
                }
            }
        }
    ]
}
```
