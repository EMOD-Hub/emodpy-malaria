# Immunity


The following parameters determine the immune system response for the disease being modeled, including
waning immunity after an infection clears.

!!! seealso
    [Full parasite genetics](malaria-model-fpg.md)
        For `PfHRP2_Boost_Rate`, `PfHRP2_Decay_Rate`, and how the Falciparum antigen variant parameters
        (`Falciparum_MSP_Variants`, `Falciparum_Nonspecific_Types`, `Falciparum_PfEMP1_Variants`) interact
        with the FPG model.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-immunity-malaria.csv", keep_default_na=False) }}
