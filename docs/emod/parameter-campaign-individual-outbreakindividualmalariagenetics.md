# OutbreakIndividualMalariaGenetics


The **OutbreakIndividualMalariaGenetics** intervention class is an individual-level intervention
that extends the [parameter-campaign-individual-outbreakindividual](parameter-campaign-individual-outbreakindividual.md) class by adding the ability
to specify parasite genetics for the infection. This class is only used when the configuration
parameter **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

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

{{ read_csv("csv/campaign-outbreakindividualmalariagenetics.csv") }}

[link](../json/parameter-campaign-individual-outbreakindividualmalariagenetics-1.json)

[link](../json/parameter-campaign-individual-outbreakindividualmalariagenetics-2.json)

[link](../json/parameter-campaign-individual-outbreakindividualmalariagenetics-3.json)
