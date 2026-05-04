# AdherentDrug


The **AdherentDrug** class is an individual-level intervention that extends
[parameter-campaign-individual-antimalarialdrug](parameter-campaign-individual-antimalarialdrug.md) class and allows for incorporating different
patterns of adherence for taking packs of anti-malarial drugs. Non-adherence means that the drugs
will not be taken on the prescribed schedule; this will lengthen the time taken to clear parasites
from the person's system, and can lengthen the duration that a feeding mosquito may become infected.


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

{{ read_csv("csv/campaign-adherentdrug.csv") }}

[link](../json/parameter-campaign-individual-adherentdrug.json)
