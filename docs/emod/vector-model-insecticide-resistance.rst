=======================
Insecticide resistance
=======================

EMOD models insecticide resistance as a genome-dependent modification of insecticide
effectiveness. When a vector with a resistant genotype encounters an insecticide-based
intervention — a bednet, indoor residual spray, or larvicide — the insecticide's killing,
blocking, and repelling effects are reduced according to resistance modifiers configured for that
genotype. This allows simulations to capture the emergence and spread of resistance alleles in
vector populations and their impact on intervention effectiveness.

Insecticide resistance operates through the vector genetics system described in
:doc:`vector-model-genetics`. Resistance alleles are defined as ordinary alleles in the ``Genes``
configuration; what makes them confer resistance is the ``Resistances`` configuration on the
insecticide that maps specific allele combinations to reduced effectiveness.


How resistance works
====================

The insecticide resistance system has three components: insecticide definitions, resistance
modifiers, and insecticide-based interventions. These are connected at runtime to produce
genome-specific intervention effects.

1. **Insecticide definitions** in config.json name each insecticide and specify which allele
   combinations confer resistance and by how much.

2. **Interventions** in campaign.json reference an insecticide by name and define time-dependent
   effectiveness profiles (waning effects) for killing, blocking, and repelling.

3. **At each time step**, when a vector encounters an intervention, the base effectiveness from the
   waning effect is multiplied by the resistance modifier for that vector's genotype. A modifier of
   1.0 means baseline susceptibility (no resistance); a modifier of 0.0 means complete resistance
   (insecticide has no effect); a modifier > 1.0 means increased susceptibility (insecticide is more effective than baseline).

For example, if a bednet has a killing effect of 0.8 and a vector's genotype has a killing
modifier of 0.5, the effective killing probability for that vector is 0.8 × 0.5 = 0.4.


Resistance types
================

Each insecticide defines resistance modifiers for four effect types that correspond to the ways
insecticide-based interventions affect vectors during the feeding cycle:

.. csv-table::
    :header: Resistance type, Description, Interventions affected
    :widths: 10, 25, 20

    Killing, "Probability that a vector dies from contact with the insecticide. Applies to individual and node interventions that have both: Killing_Config and Insecticide_Name parameters.", "**Individual interventions**: IRSHousingModification, MultiInsecticideIRSHousingModification, IndoorIndividualEmanator, Ivermectin, ScreeningHousingModification, SimpleBednet, SimpleHousingModification, UsageDependentBednet,MultiInsecticideUsageDependentBednet; Node interventions: AnimalFeedKill, IndoorSpaceSpraying, MultiInsecticideIndoorSpaceSpraying, OutdoorNodeEmanator, OutdoorRestKill, SpaceSpraying, MultiInsecticideSpaceSpraying, SugarTrap;"
    Blocking, "Probability that a vector is blocked from a blood meal. Applies to bednets blocking feeding attempts.", "**Individual interventions**: SimpleBednet, UsageDependentBednet, MultiInsecticideUsageDependentBednet; **Node interventions**: None;"
    Repelling, "Probability that a vector is deterred from entering a house or approaching a host. Applies to individual and node interventions that have both: Repelling_Config and Insecticide_Name parameters.", "**Individual interventions**: IRSHousingModification, MultiInsecticideIRSHousingModification, IndoorIndividualEmanator, ScreeningHousingModification, SimpleBednet, SimpleHousingModification, SimpleIndividualRepellent, SpatialRepellentHousingModification, UsageDependentBednet, MultiInsecticideUsageDependentBednet; **Node interventions**: OutdoorNodeEmanator, SpatialRepellent;"
    Larval_Killing, "Probability that larvae are killed by larvicide. Applies to larval habitat treatments.", "**Individual interventions**: None; **Node interventions**: Larvicides;"

A resistance modifier of 1.0 means the vector is fully susceptible — the insecticide works at
full strength. A modifier less than 1.0 means the vector has partial resistance — the insecticide
is less effective. A modifier of 0.0 means complete resistance. Modifiers greater than 1.0 are also possible, representing increased susceptibility (for example, a mutation that makes the insecticide more effective than baseline).


Configuring insecticide resistance parameters
=============================================

Insecticides are defined in the ``Insecticides`` array in config.json, at the same level as
``Vector_Species_Params``.  Each insecticide has a unique **Name** and a
**Resistances** array. Each entry in the **Resistances** array specifies a **Species**, the
**Allele_Combinations** that confer resistance, and modifier values for each effect type.

.. include:: ../reuse/warning-case.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/config-insecticides-malaria.csv

Example:
.. code-block:: json

.. literalinclude:: ../json/config-insecticides.json
   :language: json

In this example, the insecticide "pyrethroid" has two resistance entries. "Arabiensis" vectors homozygous for
the ``kdr`` allele (``kdr/kdr``) have strong resistance to killing of adults and larva (modifiers 0.1 and 0.3 respectively, meaning only
10% or 30% of the baseline killing effect applies), moderate resistance to blocking (modifier 0.8) and no resistance to repelling (modifier 1.0).
Heterozygous "funestus" vectors carrying one ``a1`` allele (matched by the wildcard ``*`` in the second
entry) have intermediate resistance to killing (modifier 0.5). Please note, being homozygous for ``a1`` (``a1/a1``) does not confer additional resistance beyond being heterozygous (``a1/wt``) because the second entry matches both genotypes with the same modifiers.

The insecticide "organophosphate" does not have any resistance entries, so all vectors are fully susceptible to it.

How effects are aggregated
==========================

When multiple insecticide-based interventions protect the same person — for example, a bednet and
IRS in the same house — their effects are aggregated at the individual level and then across the
node's population. The aggregation uses independent probability combination:

.. math::

    P_{combined} = 1 - (1 - P_1)(1 - P_2) \cdots (1 - P_n)

where each :math:`P_i` is the genome-specific probability from one intervention. This means a
vector encountering both a bednet and IRS faces the combined (but not simply additive) probability
of being killed, blocked, or repelled by either intervention.

The genome-specific probability is resolved at the final step, when the population-averaged
intervention effects are applied to a specific vector cohort. At that point, the probability is
looked up for the vector's exact genotype: if it matches a resistant allele combination, the
reduced modifier is used; otherwise the default (1.0, full susceptibility) applies.


Effect on the feeding cycle
===========================

Insecticide effects are applied during the vector feeding cycle described in
:doc:`vector-model-transmission`. Each feeding attempt branches through a decision tree where the
vector may be repelled, blocked, killed, or successfully feed. Insecticide resistance modifies
the probabilities at each branch point.

For indoor-feeding vectors, the sequence is:

1. **Repelling**: The vector may be deterred from entering the house (IRS repelling, bednet
   repelling, spatial repellents). Resistant vectors are less likely to be repelled.

2. **Blocking**: If not repelled, the vector may be blocked from feeding (bednet blocking).
   Resistant vectors are more likely to penetrate the net.

3. **Killing during feeding**: The vector may die during the feeding attempt (bednet killing).

4. **Killing after feeding**: The vector may die after feeding (IRS killing, bednet post-feed
   killing).

At each step, the probability is genome-specific: a resistant vector faces lower killing and
blocking probabilities than a susceptible vector encountering the same interventions.

For larvae, insecticide resistance modifies the larvicide killing probability. When a habitat is
treated, the larval mortality rate is increased by the larvicide effect. Larvae with resistant
genotypes experience a reduced mortality increase, proportional to their ``Larval_Killing_Modifier``.


Modeling resistance dynamics
============================

Insecticide resistance in EMOD is not a fixed property — it emerges and spreads through the
population via the same genetic inheritance system used for all vector traits. A typical workflow
for modeling resistance dynamics involves:

1. **Define resistance alleles** as part of the species' ``Genes`` configuration, with initial
   frequencies reflecting baseline resistance prevalence.

2. **Define fitness costs** (optional) using ``Gene_To_Trait_Modifiers`` to associate resistance
   alleles with increased mortality or reduced fecundity in the absence of insecticide pressure.
   This creates a fitness trade-off that prevents resistance from fixing in the population without
   selection pressure.

3. **Configure insecticides** with ``Resistances`` that map the resistance alleles to reduced
   intervention effectiveness.

4. **Deploy interventions** via campaign events. Selection pressure from the interventions favors
   resistant genotypes, increasing resistance allele frequency over time.

5. **Track resistance** using :doc:`software-report-vector-genetics` to monitor allele frequencies
   and genotype distributions across time and space.

For example, a simulation might define a ``kdr`` allele at 5% initial frequency with a 10%
fitness cost (``MORTALITY`` modifier of 1.1), then deploy pyrethroid-based bednets. Over time, the
selection pressure from bednets increases the ``kdr`` allele frequency despite the fitness cost.
Switching to a non-pyrethroid insecticide removes the selection pressure, and the fitness cost
causes the ``kdr`` frequency to decline.


Configuration example
=====================

The following is a complete example showing the configuration of a resistance allele, an
insecticide with resistance modifiers, a fitness cost, and a bednet intervention that uses the
insecticide.

**config.json** (relevant excerpts):

.. code-block:: json

    {
        "Vector_Species_Params": [
            {
                "Name": "gambiae",
                "Genes": [
                    {
                        "Is_Gender_Gene": 1,
                        "Alleles": [
                            { "Name": "X", "Initial_Allele_Frequency": 0.75, "Is_Y_Chromosome": 0 },
                            { "Name": "Y", "Initial_Allele_Frequency": 0.25, "Is_Y_Chromosome": 1 }
                        ]
                    },
                    {
                        "Alleles": [
                            { "Name": "wt", "Initial_Allele_Frequency": 0.95 },
                            { "Name": "kdr", "Initial_Allele_Frequency": 0.05 }
                        ]
                    }
                ],
                "Gene_To_Trait_Modifiers": [
                    {
                        "Allele_Combinations": [
                            [ "kdr", "kdr" ]
                        ],
                        "Trait_Modifiers": [
                            { "Trait": "MORTALITY", "Modifier": 1.1 }
                        ]
                    }
                ]
            }
        ],
        "Insecticides": [
            {
                "Name": "pyrethroid",
                "Resistances": [
                    {
                        "Species": "gambiae",
                        "Allele_Combinations": [
                            [ "kdr", "kdr" ]
                        ],
                        "Killing_Modifier": 0.1,
                        "Blocking_Modifier": 0.8,
                        "Repelling_Modifier": 1.0,
                        "Larval_Killing_Modifier": 0.3
                    },
                    {
                        "Species": "gambiae",
                        "Allele_Combinations": [
                            [ "kdr", "*" ]
                        ],
                        "Killing_Modifier": 0.5,
                        "Blocking_Modifier": 0.9,
                        "Repelling_Modifier": 1.0,
                        "Larval_Killing_Modifier": 0.6
                    }
                ]
            }
        ]
    }

**campaign.json** (relevant excerpt):

.. code-block:: json

    {
        "Events": [
            {
                "class": "CampaignEvent",
                "Start_Day": 365,
                "Event_Coordinator_Config": {
                    "class": "StandardInterventionDistributionEventCoordinator",
                    "Intervention_Config": {
                        "class": "SimpleBednet",
                        "Insecticide_Name": "pyrethroid",
                        "Killing_Config": {
                            "class": "WaningEffectExponential",
                            "Initial_Effect": 0.8,
                            "Decay_Time_Constant": 730
                        },
                        "Blocking_Config": {
                            "class": "WaningEffectExponential",
                            "Initial_Effect": 0.6,
                            "Decay_Time_Constant": 730
                        }
                    }
                }
            }
        ]
    }

With this configuration:

- Wild-type vectors (``wt/wt``) experience full bednet effects (killing = 0.8, blocking = 0.6)
  and no fitness cost.
- Heterozygous vectors (``kdr/wt``) experience reduced killing (0.8 × 0.5 = 0.4) and slightly
  reduced blocking (0.6 × 0.9 = 0.54), with no fitness cost.
- Homozygous resistant vectors (``kdr/kdr``) experience strongly reduced killing
  (0.8 × 0.1 = 0.08) and reduced blocking (0.6 × 0.8 = 0.48), but have a 10% higher mortality
  rate from the fitness cost.


Output
======

Insecticide resistance dynamics can be tracked through several reports:

- :doc:`software-report-vector-genetics` — monitors allele frequencies and genotype counts over
  time, allowing direct observation of resistance allele spread.
- The standard **InsetChart** report tracks population-level metrics such as vector counts and
  human biting rates, which reflect the aggregate impact of resistance on intervention
  effectiveness.

See :doc:`software-report-vector-genetics` for configuration details and output format.
