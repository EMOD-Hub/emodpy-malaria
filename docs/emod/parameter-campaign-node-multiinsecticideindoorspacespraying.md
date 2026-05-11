# MultiInsecticideIndoorSpaceSpraying


The **MultiInsecticideIndoorSpaceSpraying** intervention class is a node-level intervention that
uses Indoor Residual Spraying (IRS) with multiple insecticides. It builds on the
[IndoorSpaceSpraying](parameter-campaign-node-indoorspacespraying.md) class by allowing for multiple insecticides, each
with their own specified killing efficacy.

The effectiveness of the intervention is combined using the following equation:

Total efficacy = 1.0 – (1.0 – efficacy_1) * (1.0 – efficacy_2) * … * (1.0 – efficacy_n)


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes, especially when targeting certain species.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die After Feeding
*  **Vector effects:** Killing
*  **Vector sexes affected:** Females only
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

{{ read_csv("csv/campaign-multiinsecticideindoorspacespraying.csv", keep_default_na=False) }}

```json
{
    "class": "MultiInsecticideIndoorSpaceSpraying",
    "Cost_To_Consumer": 1.0,
    "Spray_Coverage": 1.0,
    "Insecticides": [
        {
            "Insecticide_Name": "pyrethroid_homo",
            "Killing_Config": {
                "Box_Duration": 100,
                "Decay_Time_Constant": 150,
                "Initial_Effect": 0.95,
                "class": "WaningEffectBoxExponential"
            }
        },
        {
            "Insecticide_Name": "carbamate_homo",
            "Killing_Config": {
                "Box_Duration": 100,
                "Decay_Time_Constant": 150,
                "Initial_Effect": 0.95,
                "class": "WaningEffectBoxExponential"
            }
        }
    ]
}
```
