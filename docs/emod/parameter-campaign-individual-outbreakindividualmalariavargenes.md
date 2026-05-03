# OutbreakIndividualMalariaVarGenes


The **OutbreakIndividualMalariaVarGenes** intervention class is an individual-level intervention
that enables infecting people with an exact set of antigens. This can be helpful when
experimenting with the immune model, such as testing how a person’s immune system
reacts if they are reinfected by the same parasite. To use this intervention, set the
configuration parameters **Malaria_Model** to MALARIA_MECHINISTIC_MODEL and **Malaria_Strain_Model**
to FALCIPARUM_FIXED_STRAIN.

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

{{ read_csv("csv/campaign-outbreakindividualmalariavargenes.csv") }}

[link](../json/parameter-campaign-individual-outbreakindividualmalariavargenes.json)
