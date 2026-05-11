# MultiInsecticideUsageDependentBednet


The **MultiInsecticideUsageDependentBednet** intervention class is an individual-level intervention
that is similar to the [UsageDependentBednet](parameter-campaign-individual-usagedependentbednet.md)
class but allows the addition of multiple insecticides.

The effectiveness of the intervention is combined using the following equation:

Total efficacy = 1.0 – (1.0 – efficacy_1) * (1.0 – efficacy_2) * … * (1.0 – efficacy_n)

At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. Insecticides can be used to target specific species or other subgroups.
*  **Time-based expiration:** No, but it will expire if the WaningEffect expires (WaningEffectRandomBox and WaningEffectMapLinear expire).
*  **Purge existing:** Yes. Adding a new bednet intervention of any type will replace any other bednet intervention in an individual. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Indoor Die Before Feeding
*  **Vector effects:** Repelling, blocking, killing
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

{{ read_csv("csv/campaign-multiinsecticideusagedependentbednet.csv", keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "MultiInsecticideUsageDependentBednet",
            "Cost_To_Consumer": 5,
            "Insecticides": [
                {
                    "Insecticide_Name": "pyrethroid",
                    "Repelling_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 300,
                        "Initial_Effect": 0.25
                    },
                    "Killing_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 300,
                        "Initial_Effect": 1.0
                    }
                },
                {
                    "Insecticide_Name": "carbamate",
                    "Repelling_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 300,
                        "Initial_Effect": 0.25
                    },
                    "Killing_Config": {
                        "class": "WaningEffectBox",
                        "Box_Duration": 300,
                        "Initial_Effect": 1.0
                    }
                }
            ],
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
