# Vector control


The following parameters determine the characteristics of campaign interventions aimed at vector
control, such as the *homing endonuclease gene (HEG)*, sugar feeding, and *Wolbachia*
infection. When, to whom, and how those interventions are distributed is determined by the
*campaign file*.


!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-vector-control-malaria.csv") }}
