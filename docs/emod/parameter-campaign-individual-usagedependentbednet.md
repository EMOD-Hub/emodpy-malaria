# UsageDependentBednet


The **UsageDependentBednet** intervention class is similar to [SimpleBednet](parameter-campaign-individual-simplebednet.md),
as it distributes insecticide-treated nets to individuals in the simulation. However,
bednet ownership and bednet usage are distinct in this intervention. As in **SimpleBednet**, net
ownership is configured through the demographic coverage, and the repelling, blocking, and killing rates of
mosquitoes are time-dependent. Use of bednets is age-dependent and can vary seasonally. Once a net
has been distributed to someone, the net usage is determined by the product of the seasonal and
age-dependent usage probabilities until the net-retention counter runs out, and the net is discarded.

While **SimpleBednet** usage is applied as a daily reduction in efficacy, **UsageDependentBednet**
uses the usage efficacy to determine whether or not the person used the net that day.  For example,
if we look at bednet with 0% repelling, 100% blocking, and 100% killing effects, and 50% usage effect,
the person with the **SimpleBednet** will have a net that has final efficacy of 50% blocking and 50% killing
each day and the person with the **UsageDependentBednet** will have half of their days with a 100% blocking and
100% killing net and half of their days with no net at all. Note that when a person migrates, they
take their net with them.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if this has already been distributed to a person.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes, especially if you want to target specific species.
*  **Time-based expiration:** Yes, an expiration timer that is independent from the waning effects can be configured.
*  **Purge existing:** Yes. Adding a new bednet intervention of any type will replace any other bednet intervention in an individual. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Indoor Die Before Feeding
*  **Vector effects:** Repelling, blocking, and killing
*  **Vector sexes affected:** Indoor meal-seeking females only.
*  **Vector life stage affected:** Adult


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

{{ read_csv("csv/campaign-usagedependentbednet.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "UsageDependentBednet",
            "Cost_To_Consumer": 5,
            "Repelling_Config": {
                "class": "WaningEffectConstant",
                "Initial_Effect": 0.0
            },
            "Blocking_Config": {
                "class": "WaningEffectConstant",
                "Initial_Effect": 1.0
            },
            "Killing_Config": {
                "class": "WaningEffectConstant",
                "Initial_Effect": 0.5
            },
            "Usage_Config_List": [
                {
                    "class": "WaningEffectMapLinearAge",
                    "Initial_Effect": 1.0,
                    "Durability_Map": {
                        "Times":  [  0.0, 12.99, 13.0, 125.0],
                        "Values": [  0.0,  0.0,   1.0,   1.0]
                    }
                },
                {
                    "class": "WaningEffectMapLinearSeasonal",
                    "Initial_Effect": 1.0,
                    "Durability_Map": {
                        "Times":  [  0.0, 20.0, 21.0, 30.0, 31.0, 365.0],
                        "Values": [  1.0,  1.0,  0.0,  0.0,  1.0,   1.0]
                    }
                }
            ],
            "Received_Event": "Bednet_Got_New_One",
            "Using_Event": "Bednet_Using",
            "Discard_Event": "Bednet_Discarded",
            "Expiration_Period_Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
            "Expiration_Period_Mean_1": 60,
            "Expiration_Period_Mean_2": 50,
            "Expiration_Period_Proportion_1": 1.0
        }
    ],
    "Use_Defaults": 1
}
```
