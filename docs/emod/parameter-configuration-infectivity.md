# Infectivity and transmission


The following parameters determine aspects of infectivity and disease transmission. For example,
how infectious individuals are and the length of time for which they remain infectious, whether the
disease can be maternally transmitted, and how population density affects infectivity.

The malaria transmission model does not use many of the parameters provided by the generic simulation
type. Instead, *gametocyte* abundances and *cytokine* mediated infectiousness are
modeled explicitly. See [Vector transmission](vector-model-transmission.md) for more information.

!!! seealso
    [Full parasite genetics](malaria-model-fpg.md)
        For `Max_Individual_Infections` and other transmission parameters as used in FPG simulations.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-infectivity-malaria.csv", keep_default_na=False) }}
