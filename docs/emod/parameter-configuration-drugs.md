# Drugs and treatments


The following parameters determine the efficacy of drugs and other treatments.

For more information on the drugs used to treat malaria, see [Antimalarial drugs](malaria-model-antimalarial-drugs.md).

!!! seealso
    [Full parasite genetics](malaria-model-fpg.md)
        For FPG drug resistance configuration, including the `Resistances` array added to `Malaria_Drug_Params` entries.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-drugs-malaria.csv", keep_default_na=False) }}
