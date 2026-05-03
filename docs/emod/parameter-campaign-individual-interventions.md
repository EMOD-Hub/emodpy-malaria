# Individual-level interventions


Individual-level interventions determine *what* will be distributed to individuals to reduce the
spread of a disease. For example, distributing vaccines or drugs are individual-level interventions.
In the schema, these are labeled as **IndividualTargeted**.  

It is also possible (but not required) to configure *why* a particular intervention is distributed
by adding trigger conditions to the intervention. For example, interventions can be triggered by
notifications broadcast after some an event, such as Births (the individual’s own
birth), GaveBirth, NewInfectionEvent, and more. It's also possible to have one intervention trigger
another intervention by asking the first intervention to broadcast a unique string, and having the
second intervention be triggered upon receipt of that string. See :doc:`parameter-campaign-event-list`.

Individual-level interventions can be used as part of configuring a cascade of care along with the individual
properties set in the demographics file. Use **Disqualifying_Properties** to disqualify individuals
who would otherwise receive the intervention and **New_Property_Value** to assign a new value when
the intervention is received. For example, you can assign a property value after receiving the
first-line treatment for a disease and prevent anyone from receiving the second-line treatment
unless they have that property value and are still symptomatic.


Vector control
==============

The following individual-level interventions are commonly used for vector control.


 .. csv-table::
   :header: "Intervention", "Target life stage", "Target biting preference", "Target biting location", "Effect"

   :doc:`parameter-campaign-individual-humanhostseekingtrap`,feeding cycle,human,,killing
   :doc:`parameter-campaign-individual-indoorindividualemanator`,feeding cycle,human,indoor,"killing, blocking"
   :doc:`parameter-campaign-individual-irshousingmodification`,feeding cycle,human,indoor,"killing, blocking"
   :doc:`parameter-campaign-individual-ivermectin`,feeding cycle,human,all,killing
   :doc:`parameter-campaign-individual-screeninghousingmodification`,feeding cycle,human,indoor,"killing, blocking"
   :doc:`parameter-campaign-individual-simplebednet`,feeding cycle,human,indoor,"killing, blocking"
   :doc:`parameter-campaign-individual-simpleindividualrepellent`,feeding cycle,human,all,blocking
   :doc:`parameter-campaign-individual-spatialrepellenthousingmodification`,feeding cycle,human,indoor,"killing, blocking"

.. taken from Jaline's wiki page,
.. https://wiki.idmod.org/pages/viewpage.action?spaceKey=EMOD&postingDay=2016%2F7%2F15&title=Vector+control+interventions+in+DTK

Summary table of individual-level interventions
===============================================

The following table provides an at-a-glance overview of the individual-level interventions.


 .. csv-table::
   :header: "Intervention", "Short description", "Able to be serialized?", "Uses insecticides", "Time-based expiration?", Purge existing?, "Vector killing contributes to:", "Vector effects"

   :doc:`parameter-campaign-individual-adherentdrug`,Model adherence with AntimalarialDrug,Y,,Y/N,,,
   :doc:`parameter-campaign-individual-antimalarialdrug`,Distribute one drug to an individual,Y,,Sort of,,,
   :doc:`parameter-campaign-individual-bitingrisk`,Adjust an individual's relative chance of getting bitten by a mosquito,Sort of,,,Sort of,,
   :doc:`parameter-campaign-individual-broadcastevent`,Send an event to an individual,,,,,,
   :doc:`parameter-campaign-individual-broadcasteventtoothernodes`,Send an event to individuals in other nodes,,,,,,
   :doc:`parameter-campaign-individual-controlledvaccine`,Manage how an individual receives a vaccine,Y,,Y,Controlled,,
   :doc:`parameter-campaign-individual-delayedintervention`,Wait before sending event or intervention,Y,,Y,,,
   :doc:`parameter-campaign-individual-humanhostseekingtrap`,Attracts and kills host-seeking mosquitoes,Y,,,Y,Indoor Die Before Feeding,"Attracting, killing"
   :doc:`parameter-campaign-individual-immunitybloodtest`,Check if an individual's immunity meets a specified threshold ,Y,,,,,
   :doc:`parameter-campaign-individual-individualimmunitychanger`,Not tested with Malaria,Y,,,,,
   :doc:`parameter-campaign-individual-irshousingmodification`,Indoor Residual Spraying for an individual,Y,Y,,Y,Indoor Die After Feeding,"Repelling, killing"
   :doc:`parameter-campaign-individual-ivcalendar`,Distribute an intervention to an indivdiual when they reach a specific age,Y,,Sort of,,,
   :doc:`parameter-campaign-individual-ivermectin`,Kill vectors feeding on human,Y,Y,Sort of,Y,Indoor/Outdoor Die After Feeding,Killing
   :doc:`parameter-campaign-individual-malariadiagnostic`,Test if an individual is infected,Y/N,,,,,
   :doc:`parameter-campaign-individual-migrateindividuals`,Schedule a trip for a single individual,Y/N,,,,,
   :doc:`parameter-campaign-individual-multieffectboostervaccine`,Not tested with Malaria,Y,,,,,
   :doc:`parameter-campaign-individual-multieffectvaccine`,Not tested with Malaria,Y,,Wanning Effect Expiration,,,
   :doc:`parameter-campaign-individual-multiinsecticideirshousingmodification`,Individual IRS involving multiple insecticides,Y,Y,,Y,Indoor Die Before/After Feeding,"Repelling, killing"
   :doc:`parameter-campaign-individual-multiinsecticideusagedependentbednet`,ITN treated with multiple insecticides,Y,Y,Y,By Name,Indoor Die Before/After Feeding,"Repelling, blocking, killing"
   :doc:`parameter-campaign-individual-multiinterventiondistributor`,Distribute multiple interventions instead of one,Y/N,,,,,
   :doc:`parameter-campaign-individual-multipackcombodrug`,Control doses of multiple drugs,Y,,,,,
   :doc:`parameter-campaign-individual-outbreakindividual`,Infect individuals,N,,,,,
   :doc:`parameter-campaign-individual-outbreakindividualmalariagenetics`,Infect individuals with a specific parasite genome,N,,,,,
   :doc:`parameter-campaign-individual-outbreakindividualmalariavargenes`,Infect individuals with specific antigen values,N,,,,,
   :doc:`parameter-campaign-individual-propertyvaluechanger`,Change an individual's **IndividualProperty** value,Y,,,,,
   :doc:`parameter-campaign-individual-rtssvaccine`,Boost CSP antibody,Y,,,,,
   :doc:`parameter-campaign-individual-screeninghousingmodification`,Modify an individual's house with screens that kill and block vectors,Y,Y,,Y,Indoor- Die Before/After Feeding,"Repelling, killing"
   :doc:`parameter-campaign-individual-simplebednet`,Insecticide Treated Net (ITN),Y,Y,Wanning Effect Expiration,By Name,Indoor- Die Before/After Feeding,"Repelling, blocking, killing"
   :doc:`parameter-campaign-individual-simpleboostervaccine`,Not tested with Malaria,Y,,,,,
   :doc:`parameter-campaign-individual-simplediagnostic`,Test if an individual is infected using sensitivity and specificity diagnostics,Y/N,,,,,
   :doc:`parameter-campaign-individual-simplehealthseekingbehavior`,Randomly distribute interventions or events to individuals,Y/N,,,,,
   :doc:`parameter-campaign-individual-simplehousingmodification`,Block & kill vectors at an individual's house,Y,Y,,Y,Indoor Die Before/After Feeding,"Repelling, killing"
   :doc:`parameter-campaign-individual-simpleindividualrepellent`,Block vectors from biting an individual,Y,Y,,,,Repelling
   :doc:`parameter-campaign-individual-simplevaccine`,"Modify the acquisition, transmission, and mortality effects by distributing a vaccine",Y,,Wanning Effect Expiration,,,
   :doc:`parameter-campaign-individual-spatialrepellenthousingmodification`,Block vectors from an individual's house,Y,Y,,Y,,Repelling
   :doc:`parameter-campaign-individual-standarddiagnostic`,Test if individuals are infected using sensitivity and specificity diagnostics,Y/N,,,,,
   :doc:`parameter-campaign-individual-usagedependentbednet`,Control when individuals use bednets (ITN),Y,Y,Y,By Name,Indoor Die Before/After Feeding,"Repelling, blocking, killing"
