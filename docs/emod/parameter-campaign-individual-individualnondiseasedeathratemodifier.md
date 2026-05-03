# IndividualNonDiseaseDeathRateModifier


The **IndividualNonDiseaseDeathRateModifier** intervention class provides a method of modifying 
an individual's non-disease mortality rate over time, until an expiration event is reached. For example, 
this intervention could be given to people who have access to health care to model that 
they have a different life expectancy than those who do not. Different distribution patterns 
can be designated, and linear interpolation will be used to calculate values between time points.

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
