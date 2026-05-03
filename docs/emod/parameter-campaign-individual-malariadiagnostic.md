# MalariaDiagnostic



The **MalariaDiagnostic** intervention class is similar to 
[parameter-campaign-individual-simplediagnostic](parameter-campaign-individual-simplediagnostic.md), but distributes a test
for malaria. There are several types of configurable diagnostic tests, and the
type selected determines the other parameters used. 

You should note that the results of **MalariaDiagnostic** can be different
than what you see in the reports.  The intervention takes an independent
measurement from the reports.  It has its own parameters that control the
sensitivity and detection threshold.


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

{{ read_csv("csv/campaign-malariadiagnostic.csv") }}

[link](../json/parameter-campaign-individual-malariadiagnostic.json)
