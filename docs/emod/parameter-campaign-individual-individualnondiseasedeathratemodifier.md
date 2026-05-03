# IndividualNonDiseaseDeathRateModifier


The **IndividualNonDiseaseDeathRateModifier** intervention class provides a method of modifying 
an individual's non-disease mortality rate over time, until an expiration event is reached. For example, 
this intervention could be given to people who have access to health care to model that 
they have a different life expectancy than those who do not. Different distribution patterns 
can be designated, and linear interpolation will be used to calculate values between time points.

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

{{ read_csv("csv/campaign-individualnondiseasedeathratemodifier.csv") }}

[link](../json/parameter-campaign-individual-individualnondiseasedeathratemodifier.json)
