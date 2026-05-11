# Insecticide resistance


EMOD models insecticide resistance as a genome-dependent modification of insecticide
effectiveness. When a vector with a resistant genotype encounters an insecticide-based
intervention — a bednet, indoor residual spray, or larvicide — the insecticide's killing,
blocking, and repelling effects are reduced according to resistance modifiers configured for that
genotype. This allows simulations to capture the emergence and spread of resistance alleles in
vector populations and their impact on intervention effectiveness.

Insecticide resistance operates through the vector genetics system described in
[Vector genetics](vector-model-genetics.md). Resistance alleles are defined as ordinary alleles in the `Genes`
configuration; what makes them confer resistance is the `Resistances` configuration on the
insecticide that maps specific allele combinations to reduced effectiveness.

Please note, once you have defined Insecticides for your simulation, you will be required to specify the
**Insecticide_Name** parameter for any intervention that has it. This is because the model needs to know
which insecticide's resistance modifiers to apply when calculating the intervention's effectiveness against
different vector genotypes. If you have interventions for which you do not wish to model resistance, you can
create a dummy insecticide with no resistance entries and reference that insecticide in those interventions.

## How resistance works


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


## Resistance types


Each insecticide defines resistance modifiers for four effect types that correspond to the ways
insecticide-based interventions affect vectors during the feeding cycle:

| Type | Description | Applicable interventions |
| --- | --- | --- |
| `Killing` | Probability that a vector dies from contact with the insecticide. Applies to interventions that have both `Killing_Config` and `Insecticide_Name` parameters. | **Individual**: IRSHousingModification, MultiInsecticideIRSHousingModification, IndoorIndividualEmanator, Ivermectin, ScreeningHousingModification, SimpleBednet, SimpleHousingModification, UsageDependentBednet, MultiInsecticideUsageDependentBednet. **Node**: AnimalFeedKill, IndoorSpaceSpraying, MultiInsecticideIndoorSpaceSpraying, OutdoorNodeEmanator, OutdoorRestKill, SpaceSpraying, MultiInsecticideSpaceSpraying, SugarTrap. |
| `Blocking` | Probability that a vector is blocked from a blood meal. Applies to bednets blocking feeding attempts. | **Individual**: SimpleBednet, UsageDependentBednet, MultiInsecticideUsageDependentBednet. **Node**: None. |
| `Repelling` | Probability that a vector is deterred from entering a house or approaching a host. Applies to interventions that have both `Repelling_Config` and `Insecticide_Name` parameters. | **Individual**: IRSHousingModification, MultiInsecticideIRSHousingModification, IndoorIndividualEmanator, ScreeningHousingModification, SimpleBednet, SimpleHousingModification, SimpleIndividualRepellent, SpatialRepellentHousingModification, UsageDependentBednet, MultiInsecticideUsageDependentBednet. **Node**: OutdoorNodeEmanator, SpatialRepellent. |
| `Larval_Killing` | Probability that larvae are killed by larvicide. Applies to larval habitat treatments. | **Individual**: None. **Node**: Larvicides. |

A resistance modifier of 1.0 means the vector is fully susceptible — the insecticide works at
full strength. A modifier less than 1.0 means the vector has partial resistance — the insecticide
is less effective. A modifier of 0.0 means complete resistance. Modifiers greater than 1.0 are also possible, representing increased susceptibility (for example, a mutation that makes the insecticide more effective than baseline).


## Configuring insecticide resistance parameters


Insecticides are defined in the `Insecticides` array in config.json, at the same level as
`Vector_Species_Params`.  Each insecticide has a unique **Name** and a
**Resistances** array. Each entry in the **Resistances** array specifies a **Species**, the
**Allele_Combinations** that confer resistance, and modifier values for each effect type.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-insecticides-malaria.csv", keep_default_na=False) }}

Example:
```json
{
    "Insecticides": [
        {
            "Name": "pyrethroid",
            "Resistances": [
                {
                    "Species": "arabiensis",
                    "Allele_Combinations": [["kdr", "kdr"]],
                    "Killing_Modifier": 0.1,
                    "Blocking_Modifier": 0.8,
                    "Repelling_Modifier": 1.0,
                    "Larval_Killing_Modifier": 0.3
                },
                {
                    "Species": "funestus",
                    "Allele_Combinations": [["a1", "*"]],
                    "Killing_Modifier": 0.5,
                    "Blocking_Modifier": 1.0,
                    "Repelling_Modifier": 1.0,
                    "Larval_Killing_Modifier": 1.0
                }
            ]
        },
        {
            "Name": "organophosphate",
            "Resistances": []
        }
    ]
}
```

In this example, the insecticide "pyrethroid" has two resistance entries. "Arabiensis" vectors homozygous for
the `kdr` allele (`kdr/kdr`) have strong resistance to killing of adults and larva (modifiers 0.1 and 0.3 respectively, meaning only
10% or 30% of the baseline killing effect applies), moderate resistance to blocking (modifier 0.8) and no resistance to repelling (modifier 1.0).
Heterozygous "funestus" vectors carrying one `a1` allele (matched by the wildcard `*` in the second
entry) have intermediate resistance to killing (modifier 0.5). Please note, being homozygous for `a1` (`a1/a1`) does not confer additional resistance beyond being heterozygous (`a1/wt`) because the second entry matches both genotypes with the same modifiers.

The insecticide "organophosphate" does not have any resistance entries, so all vectors are fully susceptible to it.

## How effects are aggregated


When multiple insecticide-based interventions protect the same person — for example, a bednet and
IRS in the same house — their effects are kept separate until they are resolved against a specific
vector cohort. Each intervention may use a different insecticide, so each one contributes its own
killing, blocking, and repelling probabilities independently. The effects are then cumulatively
applied using independent probability combination:

$$P_{combined} = 1 - (1 - P_1)(1 - P_2) \cdots (1 - P_n)$$

where each $P_i$ is the genome-specific probability from one intervention. Because each
intervention's insecticide has its own resistance modifiers, the effective probability $P_i$
depends on the vector's genotype — a vector resistant to pyrethroids but susceptible to
organophosphates will experience reduced killing from a pyrethroid bednet but full killing from
an organophosphate IRS. Two vectors with different genotypes encountering the same combination
of interventions will therefore be affected differently.

The genome-specific probability is resolved at the final step, when the intervention effects are
applied to a specific vector cohort. At that point, each intervention's probability is looked up
for the vector's exact genotype: if it matches a resistant allele combination for that
intervention's insecticide, the reduced modifier is used; otherwise the default (1.0, full
susceptibility) applies. The per-intervention probabilities are then combined as shown above.


## Effect on the vector population


Most insecticide-based interventions target only meal-seeking female vectors — those actively
host-seeking or attempting to feed. This includes bednets (SimpleBednet, UsageDependentBednet),
indoor residual spraying (IRSHousingModification), ivermectin (Ivermectin), and indoor emanators
(IndoorIndividualEmanator).

However, some interventions affect vectors beyond the meal-seeking population, including
non-meal-seeking females and males:

- **OutdoorNodeEmanator** — can kill both male and female vectors in outdoor spaces, regardless
  of host-seeking status.
- **SugarTrap** — targets both male and female vectors that feed on sugar sources, regardless
  of host-seeking status.
- **OutdoorRestKill** — kills vectors resting outdoors, including males.
- **SpaceSpraying** (and MultiInsecticideSpaceSpraying) — applies insecticide to all vectors
  present in the node, affecting males and females regardless of feeding status.

This distinction is important when modeling resistance dynamics: interventions that affect the
entire vector population exert broader selection pressure on resistance alleles than those
targeting only meal-seeking females.


## Effect on the feeding cycle


Insecticide effects are applied during the vector feeding cycle described in
[Vector transmission](vector-model-transmission.md). Each feeding attempt branches through a decision tree where the
vector may be repelled, blocked, killed, or successfully feed. Insecticide resistance modifies
the probabilities at each branch point.

For indoor-feeding vectors, the sequence is:

1. **Repelling**: The vector may be deterred from entering the house (IRS repelling, bednet
   repelling, spatial repellents). Resistant vectors are less likely to be repelled.

2. **Blocking**: If not repelled, the vector may be blocked from feeding (bednet blocking).
   Resistant vectors are more likely to penetrate the net.

3. **Killing before feeding**: If blocked, the vector then may be killed by insecticide (bednet killing).

4. **Killing after feeding**: The vector may die after feeding due to resting or Ivermectin.

At each step, the probability is genome-specific: a resistant vector faces lower killing and
blocking probabilities than a susceptible vector encountering the same interventions.

For larvae, insecticide resistance modifies the larvicide killing probability. When a habitat is
treated, the larval mortality rate is increased by the larvicide effect. Larvae with resistant
genotypes experience a reduced mortality increase, proportional to their `Larval_Killing_Modifier`.


## Modeling resistance dynamics


Insecticide resistance in EMOD depends on the genetics defined in the simulation. The mosquitoes
with the resistant alleles are more likely to survive and feed than the other mosquitoes, therefore
they will be more likely to lay eggs (if female) and more likely to mate (if male) spreading their
genes to the next generation.

A typical workflow for modeling resistance dynamics involves:

1. **Define resistance alleles** as part of the species' `Genes` configuration, with initial
   frequencies reflecting baseline resistance prevalence.

2. **Define fitness costs if any** (optional). Sometimes the resistance alleles might have a fitness
   cost such as increased mortality or reduced fecundity, which creates a trade-off that prevents
   resistance from fixing in the population without selection pressure. To model that, you can use
   `Gene_To_Trait_Modifiers` to define fitness cost traits associated with the same genes that
   have insecticide resistance.

3. **Configure insecticides** with `Resistances` that map the resistance alleles to reduced
   intervention effectiveness.

4. **Deploy interventions** via campaign events. Selection pressure from the interventions favors
   resistant genotypes, increasing resistance allele frequency over time.

5. **Track resistance** using [ReportVectorGenetics](software-report-vector-genetics.md) to monitor allele frequencies
   and genotype distributions across time and space.

For example, a simulation might define a `kdr` allele at 5% initial frequency with a 10%
fitness cost (`MORTALITY` modifier of 1.1), then deploy pyrethroid-based bednets. Over time, the
selection pressure from bednets increases the `kdr` allele frequency despite the fitness cost.
Switching to a non-pyrethroid insecticide removes the selection pressure, and the fitness cost
causes the `kdr` frequency to decline.


## Configuration example


The following is a complete example showing the configuration of a resistance allele, an
insecticide with resistance modifiers, a fitness cost, and a bednet intervention that uses the
insecticide.

Note: When calculating resistance effects based on the alleles present in a vector, more specifically
defined resistances are applied first, and each allele can contribute to a resistance effect only once.
For example, if a vector has the genotype (a1, a1) and there are resistance effects defined for both `(a1, *)`
and (a1, a1), the (a1, a1) effect will be applied because it is the more specific match. The `(a1, *)`
effect will not be applied, since both alleles have already been accounted for.

**config.json** (relevant excerpts):

```json
{
    "Vector_Species_Params": [
        {
            "Name": "gambiae",
            "Genes": [
                {
                    "Is_Gender_Gene": 0,
                    "Alleles": [
                        {"Name": "wt",  "Initial_Allele_Frequency": 0.95, "Is_Y_Chromosome": 0},
                        {"Name": "kdr", "Initial_Allele_Frequency": 0.05, "Is_Y_Chromosome": 0}
                    ]
                }
            ],
            "Gene_To_Trait_Modifiers": [
                {
                    "Allele_Combinations": [["kdr", "kdr"]],
                    "Trait_Modifiers": [{"Trait": "MORTALITY", "Modifier": 1.1}]
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
                    "Allele_Combinations": [["kdr", "kdr"]],
                    "Killing_Modifier": 0.1,
                    "Blocking_Modifier": 0.8,
                    "Repelling_Modifier": 1.0,
                    "Larval_Killing_Modifier": 0.3
                },
                {
                    "Species": "gambiae",
                    "Allele_Combinations": [["kdr", "*"]],
                    "Killing_Modifier": 0.5,
                    "Blocking_Modifier": 0.9,
                    "Repelling_Modifier": 1.0,
                    "Larval_Killing_Modifier": 0.6
                }
            ]
        }
    ]
}
```

**campaign.json** (relevant excerpt):

```json
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
                        "Decay_Time_Constant": 400
                    },
                    "Blocking_Config": {
                        "class": "WaningEffectExponential",
                        "Initial_Effect": 0.6,
                        "Decay_Time_Constant": 750
                    },
                    "Repelling_Config": {
                        "class": "WaningEffectExponential",
                        "Initial_Effect": 0.2,
                        "Decay_Time_Constant": 300
                    }
                }
            }
        }
    ]
}
```

With this configuration:

- Wild-type vectors (`wt/wt`) experience full bednet effects (initially at killing = 0.8, blocking = 0.6, repelling = 0.2)
  and no fitness cost.
- Heterozygous vectors (`kdr/wt`) experience reduced killing (0.8 × 0.5 = 0.4) and slightly
  reduced blocking (0.6 × 0.9 = 0.54), with no fitness cost.
- Homozygous resistant vectors (`kdr/kdr`) experience strongly reduced killing
  (0.8 × 0.1 = 0.08) and reduced blocking (0.6 × 0.8 = 0.48), but have a 10% higher mortality
  rate from the fitness cost.


## Output


Insecticide resistance dynamics can be tracked through the following reports:

- [ReportVectorGenetics](software-report-vector-genetics.md) — monitors allele frequencies and genotype counts over
  time, allowing direct observation of resistance allele spread.
- [InsetChart report](software-report-inset-chart.md) —  tracks population-level metrics such as vector counts and
  human biting rates, which reflect the aggregate impact of resistance on intervention
  effectiveness.
