================
Vector genetics
================

EMOD's vector genetics system models the inheritance and phenotypic effects of genetic loci in
mosquito populations. It enables simulations of Mendelian inheritance, insecticide resistance,
gene drives, sex-ratio distortion, and genetically modified mosquito releases — all operating
within the standard vector lifecycle described in :doc:`vector-model-transmission`.

Vector genetics is configured per species under ``Vector_Species_Params`` in config.json. Each
species defines its own set of genes, alleles, trait modifiers, and (optionally) gene drives.
The system does not require a separate simulation type — it is available whenever the simulation
includes vector population dynamics (``Simulation_Type`` set to VECTOR_SIM or MALARIA_SIM).


Genome representation
=====================

Each mosquito carries a diploid genome (``VectorGenome``) composed of two gametes — one
inherited from each parent (maternal and paternal). A gamete (``VectorGamete``) is a compact
32-bit integer that bit-packs allele values for up to 9 genetic loci along with Wolbachia and
microsporidia status. Both classes are marked ``final`` to prevent virtual methods, keeping memory
overhead to 4 bytes per gamete and 8 bytes per genome — critical when the simulation tracks
hundreds of millions of mosquitoes.

The 32-bit gamete layout is:

.. code-block:: none

    (upper)  WW mmm HHH ggg FFF EEE DDD CCC BBB AAA yGG (lower)

    Bits 0-2     Locus 0 (gender): GG = allele index, y = Y-chromosome flag
    Bits 3-5     Locus 1 (gene A)
    Bits 6-8     Locus 2 (gene B)
    Bits 9-11    Locus 3 (gene C)
    Bits 12-14   Locus 4 (gene D)
    Bits 15-17   Locus 5 (gene E)
    Bits 18-20   Locus 6 (gene F)
    Bits 21-23   Locus 7 (gene g)
    Bits 24-26   Locus 8 (gene H)
    Bits 27-29   Microsporidia strain index (mmm)
    Bits 30-31   Wolbachia status (WW)

Each non-gender locus stores a 3-bit allele index, supporting up to 8 alleles per gene. The
gender locus (always locus 0) uses 3 bits, but bit 2 (the ``y`` flag, mask ``0x00000004``)
distinguishes X-chromosome alleles (indices 0--3, bit 2 = 0) from Y-chromosome alleles (indices
4--7, bit 2 = 1). A mosquito's sex is determined by whether the *paternal* gamete has the
Y-chromosome flag set: if it does, the mosquito is male; otherwise it is female.

The full diploid genome is packed into a single 64-bit integer (``VectorGameteBitPair_t``) for
efficient storage and comparison: the maternal gamete occupies the lower 32 bits and the
paternal gamete the upper 32 bits. Querying a locus returns the allele index pair from both
gametes — for example, ``(0, 1)`` at locus 2 means the maternal gamete carries allele 0 and the
paternal gamete carries allele 1 at that locus.

Wolbachia and microsporidia status bits are stored identically in both gametes of a genome,
since these are cytoplasmic factors rather than Mendelian loci. Wolbachia encodes four states
(none, strain A, strain B, or both). Microsporidia encodes a strain index (0 = none).


Genes and alleles
=================

Genes are defined in the ``Genes`` array within each species' configuration. Each gene declares a
set of named alleles with initial population frequencies to be used at simulation initialization if
starting with the usual vector population of 10,000 vectors per species.

.. code-block:: json

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
                        { "Name": "a0", "Initial_Allele_Frequency": 0.9, "Is_Y_Chromosome": 0 },
                        { "Name": "a1", "Initial_Allele_Frequency": 0.1, "Is_Y_Chromosome": 0 }
                    ]
                }
            ]
        }
    ]

**Gender gene**: If defined, the gender gene must be listed first. It partitions alleles into
X-chromosome alleles (``Is_Y_Chromosome`` = 0 (false)) and Y-chromosome alleles
(``Is_Y_Chromosome`` = 1 (true)). If no gender gene is explicitly defined, EMOD creates a default
one with a single X allele and a single Y allele, with XX and XY combinations being generated at
about 50/50 frequencies.

**Constraints**: Allele names must be unique across all genes within a species. Frequencies within
a gene must sum to 1.0. A species may define at most 9 genes (including the gender gene) and at
most 8 alleles per gene.

When the simulation initializes, the vector population is seeded with genomes drawn from the
configured allele frequencies. Each gamete's alleles are sampled independently at each locus, then
maternal and paternal gametes are combined to produce diploid genomes. The resulting genotype
frequencies follow Hardy-Weinberg expectations.


Mating
======

Alleles are spread through the population via mating. Females mate exactly once in their
lifetime, when they transition from immature to adult. Males are available for mating every day.
During the immature-to-adult transition, immature males are updated first to determine how many
of each genome are available in the male queue. Female cohorts then select mates randomly from
the available males, weighted by population count.

Each female stores her mate's genome for the duration of her life. When she completes a feeding
cycle and is ready to oviposit, the stored mate genome is used to determine offspring genotypes
through the fertilization process described below.

Males have a separate life expectancy controlled by the ``Male_Life_Expectancy`` parameter
(default 10 days), independent of the female ``Adult_Life_Expectancy``. The ``MORTALITY`` trait
modifier applies to both sexes.


Mendelian inheritance
=====================

During fertilization, offspring genomes are determined through standard Mendelian segregation:

1. **Gamete creation (meiosis)**: For each locus in a parent's diploid genome, if the parent is
   homozygous (both alleles identical), all gametes carry that allele. If heterozygous, each
   gamete receives one of the two alleles with equal probability (50/50 segregation). Loci
   segregate independently.

2. **Gender determination**: Females always produce X-bearing gametes. Males produce X-bearing or
   Y-bearing gametes, with the ratio controlled by the ``FEMALE_EGG_RATIO`` trait modifier
   (default 1.0 = 50/50 sex ratio). A modifier of 2.0 produces all-female offspring; a modifier
   of 0.0 produces all-male offspring.

3. **Fertilization**: All possible combinations of maternal and paternal gametes are enumerated.
   Each combination has a probability equal to the product of the individual gamete probabilities.
   The total number of eggs is distributed across these combinations using multinomial sampling,
   producing a stochastic count for each offspring genotype. Both male and female eggs are
   produced — the ``Egg_Batch_Size`` includes both sexes.

4. **Egg cohort creation**: Offspring with the same genome are grouped into cohorts. These cohorts
   enter the egg queue and progress through the standard larval development pipeline. Crowding,
   survival rates, and development delay apply to both male and female eggs.


Germline mutations
==================

Alleles can mutate during gametogenesis, producing new allele variants in offspring at a
configured per-generation rate. Mutations are defined per gene:

.. code-block:: json

    "Genes": [
        {
            "Alleles": [
                { "Name": "a0", "Initial_Allele_Frequency": 0.95 },
                { "Name": "a1", "Initial_Allele_Frequency": 0.05 }
            ],
            "Mutations": [
                {
                    "Mutate_From": "a0",
                    "Mutate_To": "a1",
                    "Probability_Of_Mutation": 0.005
                }
            ]
        }
    ]

When gametes are created, each allele has the configured probability of mutating to the specified
target. The mutation is applied after standard Mendelian segregation but before fertilization.
Multiple mutations can be defined for a single gene, including bidirectional mutations.


.. _trait-modifiers:

Trait modifiers
===============

Trait modifiers map allele combinations to phenotypic effects. They are the mechanism by which
genotype influences mosquito biology — controlling traits such as mortality, fecundity,
insecticide susceptibility, and parasite transmission.

Each modifier specifies one or more ``Allele_Combinations`` (the genotypes it applies to) and one
or more ``Trait_Modifiers`` (the traits it affects and by how much):

.. code-block:: json

    "Gene_To_Trait_Modifiers": [
        {
            "Allele_Combinations": [
                [ "a1", "a1" ]
            ],
            "Trait_Modifiers": [
                { "Trait": "MORTALITY", "Modifier": 1.5 }
            ]
        }
    ]

In this example, mosquitoes homozygous for ``a1`` at a given locus have 1.5x the baseline
mortality rate.

**Allele combination syntax**: Each combination is a list of allele names — two per locus (one for
each gamete). ``"*"`` acts as a wildcard matching any allele. For a gene with alleles ``a0`` and
``a1``:

- ``["a1", "a1"]`` — matches only ``a1/a1`` homozygotes
- ``["a1", "*"]`` — matches any mosquito carrying at least one ``a1`` allele
- ``["*", "*"]`` — matches all genotypes (wildcard at both positions)

Multi-locus combinations list allele pairs for each relevant locus. Loci not mentioned are treated
as wildcards.

When multiple modifiers apply to the same trait for a given genome, their values are multiplied
together.


Available traits
----------------

The following traits can be modified by genotype:

.. csv-table::
    :header: Trait, Default modifier, Description
    :widths: 12, 8, 35

    INFECTED_BY_HUMAN, 1.0, "Multiplier on the probability that a mosquito becomes infected when feeding on an infectious human. Applied to the species-level ``Acquire_Modifier`` parameter."
    FECUNDITY, 1.0, "Multiplier on the number of eggs laid per oviposition. Applied to the ``Egg_Batch_Size`` parameter. This impacts egg count before egg crowding takes effect."
    FEMALE_EGG_RATIO, 1.0, "Controls the sex ratio of offspring. A value of 1.0 produces 50/50 male/female. Values above 1.0 bias toward female; values below 1.0 bias toward male. At 2.0 all offspring are female; at 0.0 all are male. Applied during fertilization after egg crowding."
    STERILITY, 1.0, "Determines if eggs are viable based on the parents' genomes. A value of 0.0 means the vector is sterile — if either parent is sterile, the eggs are not viable and are not added to the egg queue. Any nonzero value means fertile. Applied after egg crowding. Sterility does not impact mating."
    TRANSMISSION_TO_HUMAN, 1.0, "Multiplier on the probability that sporozoites in the salivary gland successfully infect a human during a bite. Applied to the species-level ``Transmission_Rate`` parameter."
    ADJUST_FERTILE_EGGS, 1.0, "Multiplier on the probability of each genome's eggs being fertile. This is the last step in the fertilization process before actual numbers of eggs are assigned. A value of 0.0 means no eggs are produced; 1.0 means no change; values above 1.0 increase egg production for that genome."
    MORTALITY, 1.0, "Multiplier on the daily mortality rate, where the base rate is ``1/Adult_Life_Expectancy`` (or ``1/Male_Life_Expectancy`` for males). Values above 1.0 increase mortality (shorter lifespan); values below 1.0 decrease it."
    INFECTED_PROGRESS, 1.0, "Multiplier on the daily progression from infected to infectious (oocyst-to-sporozoite conversion rate)."
    OOCYST_PROGRESSION, 1.0, "Additional multiplier on temperature-dependent oocyst maturation. Only applies when the vector carries a parasite matching a specified barcode (requires Full Parasite Genetics). This is an additional multiplier on top of INFECTED_PROGRESS."
    SPOROZOITE_MORTALITY, 1.0, "Multiplier on sporozoite death rate within the vector. Only applies when the vector carries a parasite matching a specified barcode (requires Full Parasite Genetics)."


.. _insecticide-resistance:

Insecticide resistance
======================

Insecticide resistance is modeled through the interaction of vector genotype with insecticide
properties. Each insecticide in the simulation defines resistance profiles that specify which
allele combinations confer resistance and how much protection they provide.

Please see :doc:`vector-model-insecticide-resistance` for more information on configuring insecticide resistance.

.. _gene-drives:

Gene drives
===========

Gene drives are genetic elements that bias their own inheritance, spreading through a population
at rates exceeding standard Mendelian expectations. EMOD supports five gene drive types, each
modeling a different mechanism.

Please see :doc:`vector-model-gene-drives` for more information on configuring gene drives.


.. _maternal-deposition:

Maternal deposition
===================

Maternal deposition models the transfer of Cas9 protein (not DNA) from mother to offspring,
generating resistance alleles in the embryo before the drive's homology-directed repair is
active. It extends gene drive behavior by adding a pre-embryonic cutting step configured in the
``Maternal_Deposition`` array within ``Vector_Species_Params``.

Please see :doc:`vector-model-maternal-deposition` for full details on how maternal deposition
works, configuration parameters, and validation rules.


Wolbachia
=========

*Wolbachia* is an intracellular bacterium that can be introduced into mosquito populations as a
disease-control strategy. EMOD models four Wolbachia states per vector: none, strain A, strain B,
or both strains A and B.

Wolbachia is inherited maternally — infected females pass their Wolbachia status to all offspring
through the egg cytoplasm. Males do not transmit Wolbachia. Wolbachia status is stored alongside
the genetic information in each gamete but is not a genetic locus — it is a cytoplasmic factor.

Wolbachia-infected males are incompatible with uninfected females: matings between Wolbachia-
carrying males and uninfected females produce inviable eggs (cytoplasmic incompatibility). This
is checked during egg laying via the ``AreWolbachiaCompatible`` function, which skips egg
production for incompatible crosses.

Wolbachia also modifies adult mortality through the ``WolbachiaMortalityModification`` parameter,
which is applied as a multiplier on the mortality rate for infected vectors.

Vectors with specific Wolbachia status can be introduced into the population using the
``MosquitoRelease`` intervention with the ``Released_Wolbachia`` parameter.


Releasing vectors with specific genomes
========================================

The ``MosquitoRelease`` intervention introduces vectors with user-specified genomes into the
simulation. This is the primary mechanism for modeling releases of genetically modified
mosquitoes, including gene drive carriers and sterile males. The user specifies the complete
genome of the released vectors — all genes and loci must be specified, including sex (via the
appropriate X/Y chromosome pair).

When gene drive alleles are released, the drive mechanics take effect during subsequent mating
and fertilization events, propagating the driven alleles through the population.

see :doc:`parameter-campaign-node-mosquitorelease` for more information on configuring mosquito releases.

Output
======

:doc:`software-report-vector-genetics` (``ReportVectorGenetics``) is the primary report for
tracking vector genetics. It produces a CSV file with vector counts stratified by genome, allele,
or allele frequency at each time step, node, and vector state (eggs, larvae, immature, adult,
infected, infectious, male).

See :doc:`software-report-vector-genetics` for full configuration details and output column
descriptions.
