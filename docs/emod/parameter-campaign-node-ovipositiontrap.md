# OvipositionTrap


The **OvipositionTrap** intervention class utilizes an oviposition trap to collect host-seeking mosquitoes, and
is based upon imposing a mortality to egg hatching from oviposition. This is a node-targeted
intervention and affects all mosquitoes living and feeding at a given node. This trap requires the
use of individual mosquitoes in the simulation configuration file (**Vector_Sampling_Type** must be
set to TRACK_ALL_VECTORS or SAMPLE_IND_VECTORS), rather than the cohort model. See [parameter-configuration-sampling](parameter-configuration-sampling.md)
configuration parameters for more information.

Notes and tips for this intervention:

*  It calculates a habitat-weighted average based on the current capacity of the habitat.  It then
   uses this average to determine if the vector dies while laying eggs.
*  A vector only lays eggs on the day she feeds.
*  In the individual model, each vector has its own timer indicating when it should feed.  If the
   number of days between feeds is configured to be temperature dependent
   (using the configuration parameter **Temperate_Dependent_Feeding_Cycle**), this duration can be
   different for each feed.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** No
*  **Time-based expiration:** No. It will continue to exist even if the efficacy is zero.
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Laying Eggs
*  **Vector effects:** Killing
*  **Vector sexes affected:** Recently-fed females only
*  **Vector life stage affected:** Adult


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-ovipositiontrap.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 140,
        "Event_Coordinator_Config": {
            "Target_Demographic": "Everyone",
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "OvipositionTrap",
                "Cost_To_Consumer": 3.75,
                "Habitat_Target": "WATER_VEGETATION",
                "Killing_Config": {
                    "class": "WaningEffectExponential",
                    "Decay_Time_Constant": 2190,
                    "Initial_Effect": 0.95
                },
                "Reduction": 0
            }
        }
    }],
    "Use_Defaults": 1
}
```
