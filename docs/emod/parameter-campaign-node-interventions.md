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


| Intervention | Target life stage | Target biting preference | Target biting location | Effect |
| --- | --- | --- | --- | --- |
| [AnimalFeedKill](parameter-campaign-node-animalfeedkill.md) | node | feeding cycle | animal | killing |
| [ArtificialDiet](parameter-campaign-node-artificialdiet.md) | feeding cycle | human | all | blocking |
| [Larvicides](parameter-campaign-node-larvicides.md) | larva | all | all | killing, reduction |
| [MosquitoRelease](parameter-campaign-node-mosquitorelease.md) |  |  |  |  |
| [SpatialRepellent](parameter-campaign-node-spatialrepellent.md) | feeding cycle | all | all | blocking |
| [OutdoorRestKill](parameter-campaign-node-outdoorrestkill.md) | "feeding cycle | males" | human | all |
| [OutdoorNodeEmanator](parameter-campaign-node-outdoornodeemanator.md) | feeding cycle, males | all | all | "repelling |
| [OvipositionTrap](parameter-campaign-node-ovipositiontrap.md) | feeding cycle | all | all | killing |
| [ScaleLarvalHabitat](parameter-campaign-node-scalelarvalhabitat.md) | larva | all | all | reduction |
| [SpaceSpraying](parameter-campaign-node-spacespraying.md) | feeding cycle | human | outdoor | killing |
| [SpatialRepellent](parameter-campaign-node-spatialrepellent.md) | feeding cycle | all | outdoor | blocking |
| [SugarTrap](parameter-campaign-node-sugartrap.md) | adults | all | all | killing |
.. taken from Jaline's wiki page,
.. https://wiki.idmod.org/pages/viewpage.action?spaceKey=EMOD&postingDay=2016%2F7%2F15&title=Vector+control+interventions+in+DTK

Summary table of node-level interventions
===============================================

The following table provides an at-a-glance overview of the node-level interventions.


| Intervention | Short description | Able to be serialized? | Uses insecticides | Time-based expiration? | Purge existing? | Vector killing contributes to: | Vector effects |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [AnimalFeedKill](parameter-campaign-node-animalfeedkill.md) | Kill vectors when feeding on animals |  | Y |  | Y | Die Before Attempting Human Feed | Killing |
| [ArtificialDiet](parameter-campaign-node-artificialdiet.md) | Kill vectors when feeding on artificial diet |  |  |  | Y |  | Attract |
| [BroadcastNodeEvent](parameter-campaign-node-broadcastnodeevent.md) | Send a node event to node |  |  |  |  |  |  |
| [IndoorSpaceSpraying](parameter-campaign-node-indoorspacespraying.md) | IRS for people within a node |  | Y |  | Y | Indoor Die After Feeding | Killing |
| [InputEIR](parameter-campaign-node-inputeir.md) | Deliver infectious bites without vectors |  |  |  | Y |  |  |
| [Larvicides](parameter-campaign-node-larvicides.md) | Kill larva in node |  | Y |  | Y | Larva | Larval killing |
| [MalariaChallenge](parameter-campaign-node-malariachallenge.md) | Deliver infectious bites or sporozoites with out vectors |  |  |  |  |  |  |
| [MigrateFamily](parameter-campaign-node-migratefamily.md) | Schedule trip for family groups in a node |  |  |  |  |  |  |
| [MosquitoRelease](parameter-campaign-node-mosquitorelease.md) | Add vectors to a node |  |  |  |  |  |  |
| [MultiInsecticideIndoorSpaceSpraying](parameter-campaign-node-multiinsecticideindoorspacespraying.md) | Node IRS involving multiple insecticides |  | Y |  | Y | Indoor Die After Feeding | Killing |
| [MultiInsecticideSpaceSpraying](parameter-campaign-node-multiinsecticidespacespraying.md) | Outdoor spraying involving multiple insecticides |  | Y |  | Y | Die Without Attempting To Feed, Die Before Attempting Human Feed | Killing |
| [MultiNodeInterventionDistributor](parameter-campaign-node-multinodeinterventiondistributor.md) | Distribute multiple interventions instead of one |  |  | Y/N |  |  |  |
| [NLHTIVNode](parameter-campaign-node-nlhtivnode.md) | Distribute node intervention on node event |  |  | Y/N |  |  |  |
| [NodeLevelHealthTriggeredIV](parameter-campaign-node-nodelevelhealthtriggerediv.md) | Distribute individual intervention on individual event |  |  | Y |  |  |  |
| [NodePropertyValueChanger](parameter-campaign-node-nodepropertyvaluechanger.md) | Change the **NodeProperty** of a node |  |  |  |  |  |  |
| [Outbreak](parameter-campaign-node-outbreak.md) | Not tested with Malaria |  |  |  |  |  |  |
| [OutdoorRestKill](parameter-campaign-node-outdoorrestkill.md) | Kill vector after feeding outdoors |  |  |  | Y | Outdoor Die After Feeding | Killing |
| [OvipositionTrap](parameter-campaign-node-ovipositiontrap.md) | Kill vector attempting to lay eggs |  |  |  | Y | Die Laying Eggs | Killing |
| [ScaleLarvalHabitat](parameter-campaign-node-scalelarvalhabitat.md) | Modify capacity of larval habitat |  |  |  | Sort of |  |  |
| [SpaceSpraying](parameter-campaign-node-spacespraying.md) | Outdoor insecticide spraying |  | Y |  | Y | Die Without Attempting To Feed, Die Before Attempting Human Feed | Killing |
| [SpatialRepellent](parameter-campaign-node-spatialrepellent.md) | Block vectors before they can attempt to feed on humans |  | Y |  | Y |  | Repelling |
| [SugarTrap](parameter-campaign-node-sugartrap.md) | kill vectors when sugar feeding |  | Y | Y | Y | Emerging, Trap Feeding | Killing |
