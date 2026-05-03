# IndoorSpaceSpraying


The **IndoorSpaceSpraying** intervention class is a node-level vector control mechanism that works
by spraying insecticides indoors. This class is similar to to
[parameter-campaign-individual-irshousingmodification](parameter-campaign-individual-irshousingmodification.md) but **IRSHousingModification** is an
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


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-indoorspacespraying.csv") }}

```json
{
    "class": "IndoorSpaceSpraying",
    "Insecticide_Name": "pyrethroid",
    "Spray_Coverage" : 0.9,
    "Killing_Config": {
        "class": "WaningEffectBoxExponential",
        "Box_Duration": 100,
        "Decay_Time_Constant": 150,
        "Initial_Effect": 1
    }
}
```
