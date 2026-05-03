# OutbreakIndividualMalariaGenetics


The **OutbreakIndividualMalariaGenetics** intervention class is an individual-level intervention
that extends the [parameter-campaign-individual-outbreakindividual](parameter-campaign-individual-outbreakindividual.md) class by adding the ability
to specify parasite genetics for the infection. This class is only used when the configuration
parameter **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

The parameter **Create_Nucleotide_Sequence_From** (see table below) determines how the parasite
genetics are defined.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-outbreakindividualmalariagenetics.csv") }}

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
        [1.00, 0.00, 0.00, 0.00],
        [0.00, 1.00, 0.00, 0.00],
        [0.00, 0.00, 1.00, 0.00],
        [0.00, 0.00, 0.00, 1.00],
        [0.50, 0.50, 0.00, 0.00],
        [0.00, 0.50, 0.50, 0.00],
        [0.00, 0.00, 0.50, 0.50],
        [0.25, 0.25, 0.25, 0.25],
        [0.10, 0.20, 0.30, 0.40],
        [0.40, 0.30, 0.20, 0.10]
    ],
    "Drug_Resistant_Allele_Frequencies_Per_Genome_Location": [
        [1.00, 0.00, 0.00, 0.00],
        [0.00, 1.00, 0.00, 0.00],
        [0.00, 0.00, 1.00, 0.00]
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
