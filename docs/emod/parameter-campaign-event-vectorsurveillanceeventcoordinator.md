# VectorSurveillanceEventCoordinator


The **VectorSurveillanceEventCoordinator** coordinator class samples the vector population
at regular intervals and reports allele frequencies or genome fractions. It is configured with
a **Counter** object that specifies the species, gender, sample size, and counting method, and
a **Responder** object that can broadcast an event each time a survey is completed. Sampling
is controlled by trigger events: the coordinator begins sampling when an event from
**Start_Trigger_Condition_List** is received, and stops when an event from
**Stop_Trigger_Condition_List** is received or the **Duration** expires.

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

{{ read_csv("csv/campaign-vectorsurveillanceeventcoordinator.csv") }}

[link](../json/parameter-campaign-event-vectorsurveillanceeventcoordinator.json)
