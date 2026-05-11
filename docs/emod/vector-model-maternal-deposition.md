# Maternal deposition


Maternal deposition models the transfer of Cas9 protein (not DNA) from mother to offspring. In
real gene drive systems, a mother carrying a Cas9 allele deposits Cas9 protein into her eggs.
After fertilization but before the embryo's own transcription activates, this maternally
deposited Cas9 can cut target alleles on the paternal chromosome via non-homologous end joining
(NHEJ). Because this occurs before homology-directed repair (HDR) is active, the cut site is
repaired imperfectly, producing resistance alleles rather than drive copies. This mechanism can
generate resistance alleles even in offspring that did not inherit the drive allele.

Maternal deposition requires gene drives to be configured — it extends the behavior of an
existing drive by adding a pre-embryonic cutting step. It is configured in the
`Maternal_Deposition` array within `Vector_Species_Params`, on the same level and separately from the
`Drivers` array. See [Gene drives](vector-model-gene-drives.md) for information on configuring gene
drives and [Vector genetics](vector-model-genetics.md) for the broader vector genetics system.


## How maternal deposition works


During the fertilization pipeline in EMOD, maternal deposition is applied after gamete creation and
germline mutations, but before gametes are combined into offspring genomes. For more details on
the EMOD fertilization pipeline, see [Mendelian inheritance](vector-model-genetics.md#mendelian-inheritance). The
sequence is:

1. **Gene drive** — applied during gamete merging (standard drive mechanics).
2. **Gamete creation** — eggs and sperm are generated from parent genomes.
3. **Germline mutations** — alleles may mutate in the gametes.
4. **Maternal deposition** — if the mother carries a Cas9-producing allele, the cutting
   likelihoods are applied to both the maternal and paternal gametes.
5. **Genome combination** — gametes are paired to form offspring genomes.

For each `Maternal_Deposition` entry, the system checks how many copies of the
`Cas9_gRNA_From` allele the mother carries at the specified locus:

- **0 copies** — no effect; maternal deposition is skipped for this entry.
- **1 copy** (heterozygous) — the cutting likelihoods are applied once to all gametes carrying
  the target allele (`Allele_To_Cut`).
- **2 copies** (homozygous) — the cutting likelihoods are applied twice in sequence. This
  produces a compound probability: if the per-allele cutting rate is *p*, the effective cutting
  rate for a homozygous mother is $1 - (1 - p)^2$. For example, a 20% per-allele cutting
  rate becomes a 36% effective rate with two copies.

The cutting converts the wild-type allele into an allele that is resistant to the gene drive —
`Cut_To_Allele` entry that matches `Allele_To_Cut` in `Likelihood_Per_Cas9_gRNA_From` represents the probability of no
effect (the allele survives uncut).


## Configuration example


```json
{
    "Maternal_Deposition": [
        {
            "Cas9_gRNA_From": "Cd",
            "Allele_To_Cut": "Aw",
            "Likelihood_Per_Cas9_gRNA_From": [
                {"Cut_To_Allele": "Aw", "Likelihood": 0.8},
                {"Cut_To_Allele": "Am", "Likelihood": 0.15},
                {"Cut_To_Allele": "Ax", "Likelihood": 0.05}
            ]
        }
    ]
}
```

In this example, we have a maternal deposition derived from an [INTEGRAL_AUTONOMOUS](vector-model-gene-drives.md#integral-autonomous) drive.
When a mother carries the drive allele `Cd`, the wild-type allele `Aw` in the gametes has a
15% chance per maternal Cas9 copy of being cut into the drive resistance allele `Am`, a 5%
chance of being cut into the drive resistance allele `Ax`, and an 80% chance of remaining
`Aw` (no effect).

If the mother is homozygous for the `Cd` allele (`Cd`/`Cd`), the maternal deposition
probabilities are applied twice to each `Aw` allele. After the first application, `Aw`
splits into `Aw` at 0.8, `Am` at 0.15, and `Ax` at 0.05. The second application acts
only on the remaining `Aw` fraction, so:

- `Aw` = 0.8 × 0.8 = 0.64
- `Am` = 0.8 × 0.15 = 0.12
- `Ax` = 0.8 × 0.05 = 0.04

The final proportions for the A-locus alleles after maternal deposition are:

- `Aw` = 0.64
- `Am` = 0.15 + 0.12 = 0.27
- `Ax` = 0.05 + 0.04 = 0.09

Multiple `Maternal_Deposition` entries can target different alleles from the same or different
Cas9 sources. Each entry is evaluated independently.


## Maternal deposition parameters


!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-maternal-deposition-malaria.csv", keep_default_na=False) }}

The following example shows a complete configuration including the gene, driver, and maternal
deposition for an *An. gambiae* population with a classic gene drive and maternal Cas9
deposition.

```json
{
    "Vector_Species_Params": [
        {
            "Name": "gambiae",
            "Genes": [
                {
                    "Is_Gender_Gene": 1,
                    "Alleles": [
                        {"Name": "X", "Initial_Allele_Frequency": 0.5, "Is_Y_Chromosome": 0},
                        {"Name": "Y", "Initial_Allele_Frequency": 0.5, "Is_Y_Chromosome": 1}
                    ]
                },
                {
                    "Is_Gender_Gene": 0,
                    "Alleles": [
                        {"Name": "Aw", "Initial_Allele_Frequency": 0.95, "Is_Y_Chromosome": 0},
                        {"Name": "Ad", "Initial_Allele_Frequency": 0.05, "Is_Y_Chromosome": 0},
                        {"Name": "Am", "Initial_Allele_Frequency": 0.0,  "Is_Y_Chromosome": 0}
                    ]
                }
            ],
            "Drivers": [
                {
                    "Driving_Allele": "Ad",
                    "Driver_Type": "CLASSIC",
                    "Alleles_Driven": [
                        {
                            "Allele_To_Copy": "Ad",
                            "Allele_To_Replace": "Aw",
                            "Copy_To_Likelihood": [
                                {"Copy_To_Allele": "Ad", "Likelihood": 0.95},
                                {"Copy_To_Allele": "Aw", "Likelihood": 0.03},
                                {"Copy_To_Allele": "Am", "Likelihood": 0.02}
                            ]
                        }
                    ]
                }
            ],
            "Maternal_Deposition": [
                {
                    "Cas9_gRNA_From": "Ad",
                    "Allele_To_Cut": "Aw",
                    "Likelihood_Per_Cas9_gRNA_From": [
                        {"Cut_To_Allele": "Aw", "Likelihood": 0.8},
                        {"Cut_To_Allele": "Am", "Likelihood": 0.2}
                    ]
                }
            ]
        }
    ]
}
```

## Validation rules


- Gene drives (`Drivers`) must be defined — maternal deposition cannot exist without a drive.
- `Cas9_gRNA_From` must match a `Driving_Allele` in the `Drivers` array.
- `Allele_To_Cut` must be an `Allele_To_Replace` for the corresponding driver.
- All `Cut_To_Allele` entries must be alleles at the same locus as `Allele_To_Cut`.
- `Cut_To_Allele` cannot be an `Allele_To_Copy` for the driver (cannot produce drive copies
  via maternal deposition).
- The `Allele_To_Cut` allele must appear as one of the `Cut_To_Allele` entries (representing
  the probability of no cutting).
- The sum of all `Likelihood` values must equal 1.0.
- No two entries may have the same `Cas9_gRNA_From` and `Allele_To_Cut` combination.
- For DAISY_CHAIN drives, `Allele_To_Cut` cannot be at the same locus as the driving allele
  (the driver cannot cut its own locus in daisy chain mode).
