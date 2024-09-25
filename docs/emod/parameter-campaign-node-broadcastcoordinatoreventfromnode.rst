=================================
BroadcastCoordinatorEventFromNode
=================================


The **BroadcastCoordinatorEventFromNode** is node-level intervention that broadcasts 
an event for coordinators. For example, if a death occurs in a node, an event can be 
broadcasted that will trigger some sort of response by the healthcare system. 
**NodeLevelHealthTriggeredIV** could be used to listen for the death of an individual and 
distribute this intervention to the node. The node intervention could then broadcast its event 
that a **TriggeredEventCoordinator** is listening for. One can use the 
**Report_Coordinator_Event_Recorder** to report on the events broadcasted by this intervention. 
Note, this coordinator class must be used with listeners that are operating on the same core. 

For more information, see :doc:`emod:dev-architecture-core`.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-broadcastcoordinatoreventfromnode.csv

.. literalinclude:: ../json/campaign-broadcastcoordinatoreventfromnode.json
   :language: json