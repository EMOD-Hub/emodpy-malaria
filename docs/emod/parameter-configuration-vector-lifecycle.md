# Vector life cycle


The following parameters determine the characteristics of the vector life cycle. Set the vector species
to include in the simulation and the feeding, egg-laying, migration, and larval development habits
of each using these parameters. The parameters for larval development related to habitat and
climate are described in [Larval configuration](parameter-configuration-larval.md).

!!! note
    Most parameters in this table are nested inside the **Vector_Species_Params** array objects,
    one object per species. The exceptions — **Enable_Egg_Mortality**, **Enable_Vector_Aging**,
    **Enable_Vector_Mortality**, **Human_Feeding_Mortality**, **Larval_Density_Dependence**,
    **Larval_Density_Mortality_Offset**, **Larval_Density_Mortality_Scalar**,
    **Vector_Sugar_Feeding_Frequency**, and **Vector_Species_Params** itself — are top-level
    config parameters.


!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
{{ read_csv("csv/config-vector-lifecycle-malaria.csv", keep_default_na=False) }}
