# IndoorSpaceSpraying


The **IndoorSpaceSpraying** intervention class is a node-level vector control mechanism that works
by spraying insecticides indoors. This class is similar to to
[IRSHousingModification](parameter-campaign-individual-irshousingmodification.md) but **IRSHousingModification** is an
individual-level intervention that uses both killing and blocking effects and
**IndoorSpaceSpraying** is a node-level intervention that uses only a killing effect. Do not use
these two interventions together. If used with **IRSHousingModification**, the **IndoorSpaceSpraying** will
override **IRSHousingModification**'s killing effect.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes, especially when targeting certain species.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die After Feeding, Indoor Die Before Feeding (when in combination with HumanHostSeekingTrap)
*  **Vector effects:** Killing
*  **Vector sexes affected:** Indoor meal-seeking females only
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

{{ read_csv("csv/campaign-indoorspacespraying.csv", keep_default_na=False) }}

```json
{
    "class": "IndoorSpaceSpraying",
    "Insecticide_Name": "pyrethroid",
    "Spray_Coverage": 0.9,
    "Killing_Config": {
        "class": "WaningEffectBoxExponential",
        "Box_Duration": 100,
        "Decay_Time_Constant": 150,
        "Initial_Effect": 1
    }
}
```
