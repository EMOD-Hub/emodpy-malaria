# MultiInsecticideIRSHousingModification


The **MultiInsecticideIRSHousingModification** intervention class is an individual-level intervention
that builds on the [parameter-campaign-individual-irshousingmodification](parameter-campaign-individual-irshousingmodification.md) class by enabling
the use of multiple insecticides. The killing efficacy of each insecticide can be specified. This class
uses Indoor Residual Spraying (IRS), where insecticide is sprayed on the interior walls of houses such that
mosquitoes resting on the walls after consuming blood meals will die.

The effectiveness of the intervention is combined using the following equation:

Total efficacy = 1.0 – (1.0 – efficacy_1) * (1.0 – efficacy_2) * … * (1.0 – efficacy_n)


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** No. Already existing intervention(s) of this class continue(s) to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die After Feeding, Indoor Die Before Feeding (when combined with HostSeekingSugarTrap)
*  **Vector effects:** Repelling and killing
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult



{% include "../reuse/warning-housing-mods.txt" %}

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-multiinsecticideirshousingmodification.csv") }}

```json
{
    "class": "MultiInsecticideIRSHousingModification",
    "Cost_To_Consumer": 1.0,
    "Insecticides": [{
            "Insecticide_Name": "pyrethroid",
            "Repelling_Config": {
                "Box_Duration": 300,
                "Initial_Effect": 0.25,
                "class": "WaningEffectBox"
            },
            "Killing_Config": {
                "Box_Duration": 300,
                "Initial_Effect": 1.0,
                "class": "WaningEffectBox"
            }
        },
        {
            "Insecticide_Name": "carbamate",
            "Repelling_Config": {
                "Box_Duration": 300,
                "Initial_Effect": 0.25,
                "class": "WaningEffectBox"
            },
            "Killing_Config": {
                "Box_Duration": 300,
                "Initial_Effect": 1.0,
                "class": "WaningEffectBox"
            }
        }
    ]
}
```
