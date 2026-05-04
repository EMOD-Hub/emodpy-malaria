# FirstNodeWithNodePropertyEventCoordinator


The **FirstNodeWithNodePropertyEventCoordinator** coordinator class screens for
a desired node property (NP) and then broadcasts a coordinator event when found. When this 
event coordinator is triggered to start, it goes through the provided list of nodes and checks 
the NPs of each. (The nodes in the provided list must be defined in the CampaignEvent's **Nodeset_Config** 
parameter.) Once a node is found with the desired NP, the coordinator event is broadcast. An additional 
coordinator event can be broadcast if the desired NP is NOT found.


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

{{ read_csv("csv/campaign-firstnodewithnodepropertyeventcoordinator.csv") }}

[link](../json/parameter-campaign-node-firstnodewithnodepropertyeventcoordinator.json)
