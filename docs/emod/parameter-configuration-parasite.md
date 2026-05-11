# Parasite dynamics


The following parameters determine the dynamics of the *Plasmodium falciparum* parasite life cycle,
including dynamics within the host and human population. For more information, see
[Infection and immunity](malaria-model-infection-immunity.md).

!!! seealso
    [Full parasite genetics](malaria-model-fpg.md)
        For the `Parasite_Genetics` parameters that configure the Full Parasite Genetics (FPG) model.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-parasite-malaria.csv", keep_default_na=False) }}
