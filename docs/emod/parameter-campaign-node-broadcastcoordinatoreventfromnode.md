# BroadcastCoordinatorEventFromNode



The **BroadcastCoordinatorEventFromNode** is node-level intervention that broadcasts 
an event for coordinators. For example, if a death occurs in a node, an event can be 
broadcasted that will trigger some sort of response by the healthcare system. 
**NodeLevelHealthTriggeredIV** could be used to listen for the death of an individual and 
distribute this intervention to the node. The node intervention could then broadcast its event 
that a **TriggeredEventCoordinator** is listening for. One can use the 
**Report_Coordinator_Event_Recorder** to report on the events broadcasted by this intervention. 
Note, this coordinator class must be used with listeners that are operating on the same core. 

For more information, see [emod:dev-architecture-core](emod:dev-architecture-core.md).

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

{{ read_csv("csv/campaign-broadcastcoordinatoreventfromnode.csv") }}

[link](../json/parameter-campaign-node-broadcastcoordinatoreventfromnode.json)
