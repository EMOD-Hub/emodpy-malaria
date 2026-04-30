===========
Gene Drives
===========

Gene drives are genetic elements that bias their own inheritance, spreading through a population
at rates exceeding standard Mendelian expectations. EMOD supports five gene drive types, each
modeling a different mechanism. Gene drives are configured in the ``Gene_Drivers`` array within each species.

Note: The model does not allow for mixing drive types.


CLASSIC
=======

The classic gene drive bundles a Cas9 endonuclease and a guide RNA (gRNA) at the same locus as
the drive allele (represented by ``Driving_Allele``). When two gametes come together during
genome formation, if one gamete has the driving allele and the other has the target allele
(``Allele_To_Replace``), the drive cuts the target and copies the driving allele into the cut
site.

The drive requires all of the following conditions to be met:

- The ``Driving_Allele`` must be present in exactly one of the two gametes (not both).
- The ``Allele_To_Replace`` for the driving allele must exist in the other gamete.
- The copy of the driving allele itself must succeed (based on ``Copy_To_Likelihood``).

If any of these conditions is not met, the entire drive fails and standard Mendelian inheritance
applies. When driving additional loci (effectors), the ``Allele_To_Copy`` must exist in the
gamete with the driving allele, and the ``Allele_To_Replace`` must exist in the other gamete.

The conversion is not perfect — the ``Copy_To_Likelihood`` parameter specifies the probability
distribution of outcomes at the cut site:

- **Successful copy**: The drive allele is copied (super-Mendelian inheritance).
- **Resistance allele**: Non-homologous end joining (NHEJ) creates a resistant allele that can no
  longer be cut, preventing future drive conversion at that locus.
- **No change**: The cut fails entirely.

Drive configuration
------------------------
A classic drive at a single locus. The ``drive_a`` allele bundles Cas9 + gRNA and copies itself
over the wild-type allele ``wild_a`` with 95% efficiency. The remaining 5% produce a resistance
allele through NHEJ:

.. code-block:: json

    "Gene_Drivers": [
        {
            "Driver_Type": "CLASSIC",
            "Driving_Allele": "drive_a",
            "Alleles_Driven": [
                {
                    "Allele_To_Copy": "drive_a",
                    "Allele_To_Replace": "wild_a",
                    "Copy_To_Likelihood": [
                        { "Copy_To_Allele": "drive_a", "Likelihood": 0.95 },
                        { "Copy_To_Allele": "resist_a", "Likelihood": 0.05 }
                    ]
                }
            ]
        }
    ]



INTEGRAL_AUTONOMOUS
===================

The integral autonomous drive separates the Cas9 (driver) and gRNA (effector) onto different
loci. Unlike the classic drive, it can drive the effector even when the driver allele itself
fails to copy. It can also drive effectors in both directions if both gametes carry the driver
allele.

The drive activates whenever at least one copy of the driver allele is present in the genome —
it does not require heterozygosity at the driven locus. For each driven locus, the
``Allele_To_Copy`` must exist in the gamete with the driving allele, and the
``Allele_To_Replace`` must exist in the other gamete. If one of these conditions is not met for
a particular locus, nothing happens at that locus, but other loci can still be driven.

Drive configuration
------------------------
An autonomous drive with one driver locus (``a1``) and one effector locus (``b1``). The driver
``a1`` copies itself over ``a0`` with 90% efficiency and also drives the effector ``b1`` over
``b0`` at 90%. Because the driver and effector are at separate loci, the effector can be driven
even if the driver allele itself fails to copy:

.. code-block:: json

    "Gene_Drivers": [
        {
            "Driver_Type": "INTEGRAL_AUTONOMOUS",
            "Driving_Allele": "a1",
            "Alleles_Driven": [
                {
                    "Allele_To_Copy": "a1",
                    "Allele_To_Replace": "a0",
                    "Copy_To_Likelihood": [
                        { "Copy_To_Allele": "a1", "Likelihood": 0.9 },
                        { "Copy_To_Allele": "a0", "Likelihood": 0.1 }
                    ]
                },
                {
                    "Allele_To_Copy": "b1",
                    "Allele_To_Replace": "b0",
                    "Copy_To_Likelihood": [
                        { "Copy_To_Allele": "b1", "Likelihood": 0.9 },
                        { "Copy_To_Allele": "b0", "Likelihood": 0.1 }
                    ]
                }
            ]
        }
    ]


DAISY_CHAIN
===========

A daisy chain drive is a multi-element system where each component drives the next in a chain,
but the first element in the chain has no drive acting on it. This creates a self-limiting drive:
the first element is lost from the population through standard Mendelian dilution, which
eventually removes the driving force from downstream elements. Daisy chain drives are modeled as
a variant of the autonomous drive with specific locus dependencies.

Drive configuration
------------------------
A two-element daisy chain. ``Ct`` (at the end of the chain) drives ``Bt`` into the population.
``Bt`` (in the middle) drives ``At``, the effector. Nothing drives ``Ct`` itself, so it is lost
through Mendelian dilution over time, making the drive self-limiting:

.. code-block:: json

    "Gene_Drivers": [
        {
            "Driver_Type": "DAISY_CHAIN",
            "Driving_Allele": "Bt",
            "Alleles_Driven": [
                {
                    "Allele_To_Copy": "At",
                    "Allele_To_Replace": "Aw",
                    "Copy_To_Likelihood": [
                        { "Copy_To_Allele": "Aw", "Likelihood": 0.0 },
                        { "Copy_To_Allele": "At", "Likelihood": 1.0 }
                    ]
                },
                {
                    "Allele_To_Copy": "Bt",
                    "Allele_To_Replace": "Bw",
                    "Copy_To_Likelihood": [
                        { "Copy_To_Allele": "Bw", "Likelihood": 1.0 }
                    ]
                }
            ]
        },
        {
            "Driver_Type": "DAISY_CHAIN",
            "Driving_Allele": "Ct",
            "Alleles_Driven": [
                {
                    "Allele_To_Copy": "Bt",
                    "Allele_To_Replace": "Bw",
                    "Copy_To_Likelihood": [
                        { "Copy_To_Allele": "Bw", "Likelihood": 0.0 },
                        { "Copy_To_Allele": "Bt", "Likelihood": 1.0 }
                    ]
                },
                {
                    "Allele_To_Copy": "Ct",
                    "Allele_To_Replace": "Cw",
                    "Copy_To_Likelihood": [
                        { "Copy_To_Allele": "Cw", "Likelihood": 1.0 }
                    ]
                }
            ]
        }
    ]


X_SHRED and Y_SHRED
===================

Sex-ratio distortion drives work by destroying (shredding) sex-chromosome-bearing gametes during
spermatogenesis. These drives only apply to gametes created from a male genome and are configured
via the ``Shredding_Alleles`` parameter block rather than ``Alleles_Driven``.

- **X_SHRED**: Destroys X-bearing sperm, biasing offspring toward males. Requires the male
  parent to carry the driving allele (``Allele_Required``) on the Y chromosome.
- **Y_SHRED**: Destroys Y-bearing sperm, biasing offspring toward females. Requires the male
  parent to carry the driving allele (``Allele_Required``) on the X chromosome.

Each shredding drive specifies:

- ``Allele_Required`` — the allele the male must carry for shredding to occur
- ``Allele_To_Shred`` — the sex-chromosome allele that is targeted for destruction
- ``Allele_To_Shred_To`` — the allele that surviving shredded gametes are converted to
- ``Allele_Shredding_Fraction`` — the fraction of targeted gametes destroyed (0.0--1.0, default
  1.0)
- ``Allele_To_Shred_To_Surviving_Fraction`` — the fraction of shredded gametes that survive as
  the ``Allele_To_Shred_To`` allele rather than being eliminated (0.0--1.0, default 0.0)


Drive configuration
--------------------

An X-shredding drive that biases offspring toward males. The drive allele ``Ad`` is at a
non-gender locus. When a male carrying ``Ad`` also has the Y-chromosome allele ``Yw``
(``Allele_Required``), his X-bearing sperm carrying ``Xw`` (``Allele_To_Shred``) are destroyed.
``Driving_Allele_Params`` specifies how the drive allele itself is inherited:

.. code-block:: json

    "Gene_Drivers": [
        {
            "Driver_Type": "X_SHRED",
            "Driving_Allele": "Ad",
            "Driving_Allele_Params": {
                "Allele_To_Copy": "Ad",
                "Allele_To_Replace": "Aw",
                "Copy_To_Likelihood": [
                    { "Copy_To_Allele": "Ad", "Likelihood": 1.0 },
                    { "Copy_To_Allele": "Aw", "Likelihood": 0.0 }
                ]
            },
            "Shredding_Alleles": {
                "Allele_Required": "Yw",
                "Allele_To_Shred": "Xw",
                "Allele_To_Shred_To": "Xm",
                "Allele_Shredding_Fraction": 1.0,
                "Allele_To_Shred_To_Surviving_Fraction": 0.0
            }
        }
    ]

With ``Allele_Shredding_Fraction`` = 1.0 and ``Allele_To_Shred_To_Surviving_Fraction`` = 0.0,
all X-bearing sperm are destroyed and none survive as the ``Xm`` allele.

**Y_SHRED example**:

A Y-shredding drive that biases offspring toward females. When a male carrying ``Ad`` also has
the X-chromosome allele ``Xw`` (``Allele_Required``), his Y-bearing sperm carrying ``Yw``
(``Allele_To_Shred``) are destroyed:

.. code-block:: json

    "Gene_Drivers": [
        {
            "Driver_Type": "Y_SHRED",
            "Driving_Allele": "Ad",
            "Driving_Allele_Params": {
                "Allele_To_Copy": "Ad",
                "Allele_To_Replace": "Aw",
                "Copy_To_Likelihood": [
                    { "Copy_To_Allele": "Ad", "Likelihood": 1.0 },
                    { "Copy_To_Allele": "Aw", "Likelihood": 0.0 }
                ]
            },
            "Shredding_Alleles": {
                "Allele_Required": "Xw",
                "Allele_To_Shred": "Yw",
                "Allele_To_Shred_To": "Ym",
                "Allele_Shredding_Fraction": 1.0,
                "Allele_To_Shred_To_Surviving_Fraction": 0.0
            }
        }
    ]
