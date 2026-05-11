# OutbreakIndividualMalariaGenetics


The **OutbreakIndividualMalariaGenetics** intervention class is an individual-level intervention
that extends the [OutbreakIndividual](parameter-campaign-individual-outbreakindividual.md) class by adding the ability
to specify parasite genetics for the infection. This class is only used when the configuration
parameter **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

!!! seealso
    [Full parasite genetics](malaria-model-fpg.md)
        For the full FPG workflow, including genome configuration, seeding modes, recombination, and output reports.

The parameter **Create_Nucleotide_Sequence_From** (see table below) determines how the parasite
genetics are defined.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv("csv/campaign-outbreakindividualmalariagenetics.csv", keep_default_na=False) }}

```json
{
    "class": "OutbreakIndividualMalariaGenetics",
    "Create_Nucleotide_Squence_From": "BARCODE_STRING",
    "Barcode_String": "ACGTACGTACGTACGTACGTACGT",
    "Drug_Resistant_String": "AAT"
}
```

```json
{
    "class": "OutbreakIndividualMalariaGenetics",
    "Create_Nucleotide_Squence_From": "ALLELE_FREQUENCIES",
    "Barcode_Allele_Frequencies_Per_Genome_Location": [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.5, 0.5, 0.0, 0.0],
        [0.0, 0.5, 0.5, 0.0],
        [0.0, 0.0, 0.5, 0.5],
        [0.25, 0.25, 0.25, 0.25],
        [0.1, 0.2, 0.3, 0.4],
        [0.4, 0.3, 0.2, 0.1]
    ],
    "Drug_Resistant_Allele_Frequencies_Per_Genome_Location": [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0]
    ]
}
```

```json
{
    "class": "OutbreakIndividualMalariaGenetics",
    "Create_Nucleotide_Squence_From": "NUCLEOTIDE_SEQUENCE",
    "Barcode_String": "ACGTACGTACGTACGTACGTACGT",
    "Drug_Resistant_String": "AAT",
    "MSP_Variant_Value": 11,
    "PfEMP1_Variants_Values": [
        1, 74, 147, 220, 293, 366, 439, 512, 585, 658,
        731, 804, 877, 950, 23, 96, 169, 242, 315, 388,
        461, 534, 607, 680, 753, 826, 899, 972, 45, 118,
        191, 264, 337, 410, 483, 556, 629, 702, 775, 848,
        921, 994, 67, 140, 213, 286, 359, 432, 505, 578
    ]
}
```
