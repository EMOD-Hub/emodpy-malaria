# Larval habitat


The following parameters determine mosquito larval development related to habitat and climate. For
more information, see [Larval habitat](vector-model-larval-habitat.md). Parameters for the vector life cycle more
broadly are described in [Vector lifecycle configuration](parameter-configuration-vector-lifecycle.md).


!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-larval-malaria.csv", keep_default_na=False) }}
