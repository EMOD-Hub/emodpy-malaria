# Node-level interventions


Node-level interventions determine *what* will be distributed to each :term:`node` to reduce the spread of a
disease. For example, spraying larvicide in a village to kill mosquito larvae is a node-level malaria
intervention. Sometimes this can be an intermediate intervention that schedules another
intervention. Node-level disease outbreaks are also configured as "interventions". In the schema,
these are labeled as **NodeTargeted**.

It is also possible (but not required) to configure *why* a particular intervention is distributed
by adding trigger conditions to the intervention. For example, interventions can be triggered by
notifications broadcast after some an event, such as Births, NewInfectionEvent, and more. It's also
possible to have one intervention trigger another intervention by asking the first intervention to
broadcast a unique string, and having the second intervention be triggered upon receipt of that
string. See :doc:`parameter-campaign-event-list`.


Vector control
==============

The following node-level interventions are commonly used for vector control.


 .. csv-table::
   :header: "Intervention", "Target life stage", "Target biting preference", "Target biting location", "Effect"

   :doc:`parameter-campaign-node-animalfeedkill`,node,feeding cycle,animal,killing
   :doc:`parameter-campaign-node-artificialdiet`,feeding cycle,human,all,blocking
   :doc:`parameter-campaign-node-larvicides`,larva,all,all,"killing, reduction"
   :doc:`parameter-campaign-node-mosquitorelease`,,,,
   :doc:`parameter-campaign-node-spatialrepellent`, feeding cycle,all ,all ,"blocking"
   :doc:`parameter-campaign-node-outdoorrestkill`, "feeding cycle, males",human,all,killing
   :doc:`parameter-campaign-node-outdoornodeemanator`,"feeding cycle, males", all,all, "repelling,killing"
   :doc:`parameter-campaign-node-ovipositiontrap`,feeding cycle,all,all,killing
   :doc:`parameter-campaign-node-scalelarvalhabitat`,larva,all,all,reduction
   :doc:`parameter-campaign-node-spacespraying`,feeding cycle,human ,outdoor ,killing
   :doc:`parameter-campaign-node-spatialrepellent`,feeding cycle,all ,outdoor ,blocking
   :doc:`parameter-campaign-node-sugartrap`,adults,all,all,killing

.. taken from Jaline's wiki page,
.. https://wiki.idmod.org/pages/viewpage.action?spaceKey=EMOD&postingDay=2016%2F7%2F15&title=Vector+control+interventions+in+DTK

Summary table of node-level interventions
===============================================

The following table provides an at-a-glance overview of the node-level interventions.


 .. csv-table::
   :header: "Intervention", "Short description", "Able to be serialized?", "Uses insecticides", "Time-based expiration?", Purge existing?, "Vector killing contributes to:", "Vector effects"

   :doc:`parameter-campaign-node-animalfeedkill`,Kill vectors when feeding on animals,,Y,,Y,Die Before Attempting Human Feed,Killing
   :doc:`parameter-campaign-node-artificialdiet`,Kill vectors when feeding on artificial diet,,,,Y,,Attract
   :doc:`parameter-campaign-node-broadcastnodeevent`,Send a node event to node,,,,,,
   :doc:`parameter-campaign-node-indoorspacespraying`,IRS for people within a node,,Y,,Y,Indoor Die After Feeding,Killing
   :doc:`parameter-campaign-node-inputeir`,Deliver infectious bites without vectors,,,,Y,,
   :doc:`parameter-campaign-node-larvicides`,Kill larva in node,,Y,,Y,Larva,Larval killing
   :doc:`parameter-campaign-node-malariachallenge`,Deliver infectious bites or sporozoites with out vectors,,,,,,
   :doc:`parameter-campaign-node-migratefamily`,Schedule trip for family groups in a node,,,,,,
   :doc:`parameter-campaign-node-mosquitorelease`,Add vectors to a node,,,,,,
   :doc:`parameter-campaign-node-multiinsecticideindoorspacespraying`,Node IRS involving multiple insecticides,,Y,,Y,Indoor Die After Feeding,Killing
   :doc:`parameter-campaign-node-multiinsecticidespacespraying`,Outdoor spraying involving multiple insecticides,,Y,,Y,"Die Without Attempting To Feed, Die Before Attempting Human Feed",Killing
   :doc:`parameter-campaign-node-multinodeinterventiondistributor`,Distribute multiple interventions instead of one,,,Y/N,,,
   :doc:`parameter-campaign-node-nlhtivnode`,Distribute node intervention on node event,,,Y/N,,,
   :doc:`parameter-campaign-node-nodelevelhealthtriggerediv`,Distribute individual intervention on individual event,,,Y,,,
   :doc:`parameter-campaign-node-nodepropertyvaluechanger`,Change the **NodeProperty** of a node,,,,,,
   :doc:`parameter-campaign-node-outbreak`,Not tested with Malaria,,,,,,
   :doc:`parameter-campaign-node-outdoorrestkill`,Kill vector after feeding outdoors,,,,Y,Outdoor Die After Feeding,Killing
   :doc:`parameter-campaign-node-ovipositiontrap`,Kill vector attempting to lay eggs,,,,Y,Die Laying Eggs,Killing
   :doc:`parameter-campaign-node-scalelarvalhabitat`,Modify capacity of larval habitat,,,,Sort of,,
   :doc:`parameter-campaign-node-spacespraying`,Outdoor insecticide spraying,,Y,,Y,"Die Without Attempting To Feed, Die Before Attempting Human Feed",Killing
   :doc:`parameter-campaign-node-spatialrepellent`,Block vectors before they can attempt to feed on humans,,Y,,Y,,Repelling
   :doc:`parameter-campaign-node-sugartrap`,kill vectors when sugar feeding,,Y,Y,Y,"Emerging, Trap Feeding",Killing
