====================
Maternal deposition
====================

Maternal deposition models the transfer of Cas9 protein (not DNA) from mother to offspring. In
real gene drive systems, a mother carrying a Cas9 allele deposits Cas9 protein into her eggs.
After fertilization but before the embryo's own transcription activates, this maternally
deposited Cas9 can cut target alleles on the paternal chromosome via non-homologous end joining
(NHEJ). Because this occurs before homology-directed repair (HDR) is active, the cut site is
repaired imperfectly, producing resistance alleles rather than drive copies. This mechanism can
generate resistance alleles even in offspring that did not inherit the drive allele.

Maternal deposition requires gene drives to be configured — it extends the behavior of an
existing drive by adding a pre-embryonic cutting step. It is configured in the
``Maternal_Deposition`` array within ``Vector_Species_Params``, on the same level and separately from the
``Drivers`` array. See :doc:`vector-model-gene-drives` for information on configuring gene
drives and :doc:`vector-model-genetics` for the broader vector genetics system.


How maternal deposition works
=============================

During the fertilization pipeline in EMOD, maternal deposition is applied after gamete creation and
germline mutations, but before gametes are combined into offspring genomes. The sequence is:

1. **Gene drive** — applied during gamete merging (standard drive mechanics).
2. **Gamete creation** — eggs and sperm are generated from parent genomes.
3. **Germline mutations** — alleles may mutate in the gametes.
4. **Maternal deposition** — if the mother carries a Cas9-producing allele, the cutting
   likelihoods are applied to both the maternal and paternal gametes.
5. **Genome combination** — gametes are paired to form offspring genomes.

For each ``Maternal_Deposition`` entry, the system checks how many copies of the
``Cas9_gRNA_From`` allele the mother carries at the specified locus:

- **0 copies** — no effect; maternal deposition is skipped for this entry.
- **1 copy** (heterozygous) — the cutting likelihoods are applied once to all gametes carrying
  the target allele (``Allele_To_Cut``).
- **2 copies** (homozygous) — the cutting likelihoods are applied twice in sequence. This
  produces a compound probability: if the per-allele cutting rate is *p*, the effective cutting
  rate for a homozygous mother is :math:`1 - (1 - p)^2`. For example, a 20% per-allele cutting
  rate becomes a 36% effective rate with two copies.

The cutting produces only resistance alleles — it cannot produce the drive allele itself. The
``Allele_To_Cut`` entry in ``Likelihood_Per_Cas9_gRNA_From`` represents the probability of no
effect (the allele survives uncut).


Configuration example
=====================

.. code-block:: json

    "Maternal_Deposition": [
        {
            "Cas9_gRNA_From": "Ad",
            "Allele_To_Cut": "Aw",
            "Likelihood_Per_Cas9_gRNA_From": [
                {
                    "Cut_To_Allele": "Aw",
                    "Likelihood": 0.8
                },
                {
                    "Cut_To_Allele": "Am",
                    "Likelihood": 0.2
                }
            ]
        }
    ]

In this example, when a mother carries the drive allele ``Ad``, the wild-type allele ``Aw`` in
the gametes has a 20% chance per maternal Cas9 copy of being cut into the resistance allele
``Am``, and an 80% chance of remaining ``Aw`` (no effect). If the mother is homozygous for
``Ad``, the effective cutting rate is :math:`1 - (0.8)^2 = 0.36` (36%).

Multiple ``Maternal_Deposition`` entries can target different alleles from the same or different
Cas9 sources. Each entry is evaluated independently.


Maternal deposition parameters
==============================

.. include:: ../reuse/warning-case.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/config-maternal-deposition-malaria.csv

The following example shows a complete configuration including the gene, driver, and maternal
deposition for an *An. gambiae* population with a classic gene drive and maternal Cas9
deposition.

.. literalinclude:: ../json/config-maternal-deposition.json
   :language: json


Validation rules
================

- Gene drives (``Drivers``) must be defined — maternal deposition cannot exist without a drive.
- ``Cas9_gRNA_From`` must match a ``Driving_Allele`` in the ``Drivers`` array.
- ``Allele_To_Cut`` must be an ``Allele_To_Replace`` for the corresponding driver.
- All ``Cut_To_Allele`` entries must be alleles at the same locus as ``Allele_To_Cut``.
- ``Cut_To_Allele`` cannot be an ``Allele_To_Copy`` for the driver (cannot produce drive copies
  via maternal deposition).
- The ``Allele_To_Cut`` allele must appear as one of the ``Cut_To_Allele`` entries (representing
  the probability of no cutting).
- The sum of all ``Likelihood`` values must equal 1.0.
- No two entries may have the same ``Cas9_gRNA_From`` and ``Allele_To_Cut`` combination.
- For DAISY_CHAIN drives, ``Allele_To_Cut`` cannot be at the same locus as the driving allele
  (the driver cannot cut its own locus in daisy chain mode).
