# NLHTIVNode


The **NLHTIVNode** intervention class distributes node-level interventions to nodes when a specific
user-defined node event occurs. For example, **NLHTIVNode** can be configured to have
**SurveillanceEventCoordinator** set to listen for **NewInfectionEvents**, and then broadcast a
node event when a certain number of events is reached, such as distributing **IndoorSpaceSpraying**
to a node with a high number of new infections.

**NLHTIVNode** is similar to [parameter-campaign-node-nodelevelhealthtriggerediv](parameter-campaign-node-nodelevelhealthtriggerediv.md) but **NLHTIVNode**
is focused on *node* interventions and events while **NodeLevelHealthTriggeredIV** is focused on
*individual* interventions and events.

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

{{ read_csv("csv/campaign-nlhtivnode.csv") }}

[link](../json/parameter-campaign-node-nlhtivnode.json)
