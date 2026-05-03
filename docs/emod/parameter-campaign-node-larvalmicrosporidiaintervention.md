# LarvalMicrosporidiaIntervention


The **LarvalMicrosporidiaIntervention** is a node-level intervention that mimics
seeding water bodies with microsporidia or other endosymbiont to infect mosquito larvae, reducing their ability to
transmit malaria. The intervention distributes a specific microsporidia strain and can be limited
to a particular larval habitat type. When no other **LarvalMicrosporidiaIntervention**s are present, 
the portion of larvae infected each day is the product of the
current **Infectivity_Config** value and **Habitat_Coverage**. The **Infectivity_Config** waning effect
can be configured to decay over time.

Multiple interventions can target larvae in the same habitat. The algorithm resolves these into a single map of strain → fraction newly infected.

Step 1: Filter

Only interventions matching the queried habitat (or ALL_HABITATS) and strains matching species are considered.

Step 2: Process each intervention sequentially

For each new intervention, the larval population is conceptually divided into two groups:

1. Already claimed by a previous strain — each previously processed strain has coverage over some fraction of the population and has been processed to be non-overlapping with other previously-processed strains. 
2. Unclaimed — the remainder not yet covered by any strain.

The new intervention's coverage reaches into both groups:

For each previously-processed strain:
- From already-claimed larvae: Where the new intervention overlaps a previous strain's coverage, the overlapping portion is
split proportionally by effect strength. If strain A has effect 0.3 and the new strain B has effect 0.7, then of the
overlapping larvae, 30% stay with A and 70% go to B. The non-overlapping portion of the previous strain's coverage (i.e., 1 − coverage of the new intervention) remains unchanged.

For unclaimed larvae: 
- The new intervention claims unclaimed × coverage.

Step 3: Merge same-strain entries

If the new intervention is distributing a previously-processed strain, their resolved coverages are summed and their effects are combined as a
coverage-weighted average:

new_coverageA = coverage_A + coverage_A1
new_effectA = (coverage_A × effect_A + coverage_A1 × effect_A1) / new_coverageA

If this is a new strain, its coverage and effect are added to the previously-processed strains.

This resolves the interventions processed so far into non-overlapping coverages with effects, one for each strain.

Step 4: Repeat for all remaining interventions

The process repeats Steps 1-3 until all the interventions matching this habitat and species are processed.

Step 5: Compute final infectivity

For each strain, the final fraction newly infected is coverage × effect.

Key properties

- Order-dependent: Processing interventions in different orders can yield different results because each new intervention
  redistributes from the current state.
- Conservation: Total coverage across all strains never exceeds 1.0 — every larva is accounted for exactly once (either
  claimed by a strain or uninfected).
- Proportional competition: When two strains overlap, the stronger effect wins a larger share, but neither fully displaces
  the other.




At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** No
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** No. Already existing intervention(s) of this class continue(s) to exist together with any new interventions of this class. Their coverages and effects are resolved per the algorithm described above.
*  **Vector killing contributes to:** Does not apply
*  **Vector effects:** Microsporidia/endosymbiont infection of larvae
*  **Vector sexes affected:** Both male and female larvae
*  **Vector life stage affected:** Larval

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

{{ read_csv("csv/campaign-larvalmicrosporidiaintervention.csv") }}

```json
{
    "Events": [{
        "class": "CampaignEvent",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 1,
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "LarvalMicrosporidiaIntervention",
                "Strain_Name": "Strain_A",
                "Habitat_Target": "ALL_HABITATS",
                "Habitat_Coverage": 1.0,
                "Infectivity_Config": {
                    "class": "WaningEffectBox",
                    "Box_Duration": 100,
                    "Initial_Effect": 0.5
                },
                "Cost_To_Consumer": 0
            }
        }
    }],
    "Use_Defaults": 1
}
```
