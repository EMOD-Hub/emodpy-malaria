# SimpleBednet


The **SimpleBednet** intervention class implements *insecticide-treated nets (ITN)* in the
simulation. ITNs are a key component of modern malaria control efforts, and have recently been
scaled up towards universal coverage in sub-Saharan Africa. Modern bednets are made of a
polyethylene or polyester mesh, which is impregnated with a slowly releasing pyrethroid insecticide.
When mosquitoes that are seeking a blood meal indoors encounter a net, the feeding attempt maybe be
repelled due to presence pf insecticides or blocked as long as the net retains its physical integrity
and has been correctly installed. Blocked feeding attempts also carry the possibility of killing the mosquito.
Net ownership is configured through the demographic coverage, and the repelling, blocking, and killing rates
of mosquitoes are time-dependent. All the efficacies are also affected by the Usage_Config parameter - the
usage effect is multiplied by the repelling, blocking, and killing effects to determine the final efficacy of the
net on any given day.

**SimpleBednet** can model the bednet usage of net owners by reducing the daily efficacy. To model
individuals using nets intermittently, see [parameter-campaign-individual-usagedependentbednet](parameter-campaign-individual-usagedependentbednet.md).
To include multiple insecticides, see [parameter-campaign-individual-multiinsecticideusagedependentbednet](parameter-campaign-individual-multiinsecticideusagedependentbednet.md).


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


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-simplebednet.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 1460,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 0.7,
            "Intervention_Config": {
                "class": "SimpleBednet",
                "Cost_To_Consumer": 3.75,
                "Repelling_Config": {
                    "Initial_Effect": 0.1,
                    "Decay_Time_Constant": 730,
                    "class": "WaningEffectExponential"
                },
                "Killing_Config": {
                    "Initial_Effect": 0.6,
                    "Decay_Time_Constant": 1460,
                    "class": "WaningEffectExponential"
                },
                "Blocking_Config": {
                    "Initial_Effect": 0.9,
                    "Decay_Time_Constant": 730,
                    "class": "WaningEffectExponential"
                },
                "Usage_Config": {
                    "class": "WaningEffectConstant",
                    "Initial_Effect": 1.0
                }
            }
        }
    }],
    "Use_Defaults": 1
}
```
