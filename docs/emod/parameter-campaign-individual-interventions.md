# Individual-level interventions

Individual-level interventions determine *what* will be distributed to individuals to reduce the
spread of a disease. For example, distributing vaccines or drugs are individual-level interventions.
In the schema, these are labeled as **IndividualTargeted**.  

It is also possible (but not required) to configure *why* a particular intervention is distributed
by adding trigger conditions to the intervention. For example, interventions can be triggered by
notifications broadcast after some an event, such as Births (the individual’s own
birth), GaveBirth, NewInfectionEvent, and more. It's also possible to have one intervention trigger
another intervention by asking the first intervention to broadcast a unique string, and having the
second intervention be triggered upon receipt of that string. See [Event list](parameter-campaign-event-list.md).

Individual-level interventions can be used as part of configuring a cascade of care along with the individual
properties set in the demographics file. Use **Disqualifying_Properties** to disqualify individuals
who would otherwise receive the intervention and **New_Property_Value** to assign a new value when
the intervention is received. For example, you can assign a property value after receiving the
first-line treatment for a disease and prevent anyone from receiving the second-line treatment
unless they have that property value and are still symptomatic.


## Vector control

The following individual-level interventions are commonly used for vector control.

| Intervention | Target life stage | Target biting preference | Target biting location | Effect |
| --- | --- | --- | --- | --- |
| [HumanHostSeekingTrap](parameter-campaign-individual-humanhostseekingtrap.md) | feeding cycle | human |  | killing |
| [IndoorIndividualEmanator](parameter-campaign-individual-indoorindividualemanator.md) | feeding cycle | human | indoor | killing, blocking |
| [IRSHousingModification](parameter-campaign-individual-irshousingmodification.md) | feeding cycle | human | indoor | killing, blocking |
| [Ivermectin](parameter-campaign-individual-ivermectin.md) | feeding cycle | human | all | killing |
| [ScreeningHousingModification](parameter-campaign-individual-screeninghousingmodification.md) | feeding cycle | human | indoor | killing, blocking |
| [SimpleBednet](parameter-campaign-individual-simplebednet.md) | feeding cycle | human | indoor | killing, blocking |
| [SimpleIndividualRepellent](parameter-campaign-individual-simpleindividualrepellent.md) | feeding cycle | human | all | blocking |
| [SpatialRepellentHousingModification](parameter-campaign-individual-spatialrepellenthousingmodification.md) | feeding cycle | human | indoor | killing, blocking |


## Summary table of individual-level interventions

The following table provides an at-a-glance overview of the individual-level interventions.

| Intervention | Short description | Able to be serialized? | Uses insecticides | Time-based expiration? | Purge existing? | Vector killing contributes to: | Vector effects |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [AdherentDrug](parameter-campaign-individual-adherentdrug.md) | Model adherence with AntimalarialDrug | Y |  | Y/N |  |  |  |
| [AntimalarialDrug](parameter-campaign-individual-antimalarialdrug.md) | Distribute one drug to an individual | Y |  | Sort of |  |  |  |
| [BitingRisk](parameter-campaign-individual-bitingrisk.md) | Adjust an individual's relative chance of getting bitten by a mosquito | Sort of |  |  | Sort of |  |  |
| [BroadcastEvent](parameter-campaign-individual-broadcastevent.md) | Send an event to an individual |  |  |  |  |  |  |
| [BroadcastEventToOtherNodes](parameter-campaign-individual-broadcasteventtoothernodes.md) | Send an event to individuals in other nodes |  |  |  |  |  |  |
| [ControlledVaccine](parameter-campaign-individual-controlledvaccine.md) | Manage how an individual receives a vaccine | Y |  | Y | Controlled |  |  |
| [DelayedIntervention](parameter-campaign-individual-delayedintervention.md) | Wait before sending event or intervention | Y |  | Y |  |  |  |
| [HumanHostSeekingTrap](parameter-campaign-individual-humanhostseekingtrap.md) | Attracts and kills host-seeking mosquitoes | Y |  |  | Y | Indoor Die Before Feeding | Attracting, killing |
| [ImmunityBloodTest](parameter-campaign-individual-immunitybloodtest.md) | Check if an individual's immunity meets a specified threshold | Y |  |  |  |  |  |
| [IndividualImmunityChanger](parameter-campaign-individual-individualimmunitychanger.md) | Not tested with Malaria | Y |  |  |  |  |  |
| [IRSHousingModification](parameter-campaign-individual-irshousingmodification.md) | Indoor Residual Spraying for an individual | Y | Y |  | Y | Indoor Die After Feeding | Repelling, killing |
| [IVCalendar](parameter-campaign-individual-ivcalendar.md) | Distribute an intervention to an indivdiual when they reach a specific age | Y |  | Sort of |  |  |  |
| [Ivermectin](parameter-campaign-individual-ivermectin.md) | Kill vectors feeding on human | Y | Y | Sort of | Y | Indoor/Outdoor Die After Feeding | Killing |
| [MalariaDiagnostic](parameter-campaign-individual-malariadiagnostic.md) | Test if an individual is infected | Y/N |  |  |  |  |  |
| [MigrateIndividuals](parameter-campaign-individual-migrateindividuals.md) | Schedule a trip for a single individual | Y/N |  |  |  |  |  |
| [MultiEffectBoosterVaccine](parameter-campaign-individual-multieffectboostervaccine.md) | Not tested with Malaria | Y |  |  |  |  |  |
| [MultiEffectVaccine](parameter-campaign-individual-multieffectvaccine.md) | Not tested with Malaria | Y |  | Wanning Effect Expiration |  |  |  |
| [MultiInsecticideIRSHousingModification](parameter-campaign-individual-multiinsecticideirshousingmodification.md) | Individual IRS involving multiple insecticides | Y | Y |  | Y | Indoor Die Before/After Feeding | Repelling, killing |
| [MultiInsecticideUsageDependentBednet](parameter-campaign-individual-multiinsecticideusagedependentbednet.md) | ITN treated with multiple insecticides | Y | Y | Y | By Name | Indoor Die Before/After Feeding | Repelling, blocking, killing |
| [MultiInterventionDistributor](parameter-campaign-individual-multiinterventiondistributor.md) | Distribute multiple interventions instead of one | Y/N |  |  |  |  |  |
| [MultiPackComboDrug](parameter-campaign-individual-multipackcombodrug.md) | Control doses of multiple drugs | Y |  |  |  |  |  |
| [OutbreakIndividual](parameter-campaign-individual-outbreakindividual.md) | Infect individuals | N |  |  |  |  |  |
| [OutbreakIndividualMalariaGenetics](parameter-campaign-individual-outbreakindividualmalariagenetics.md) | Infect individuals with a specific parasite genome | N |  |  |  |  |  |
| [OutbreakIndividualMalariaVarGenes](parameter-campaign-individual-outbreakindividualmalariavargenes.md) | Infect individuals with specific antigen values | N |  |  |  |  |  |
| [PropertyValueChanger](parameter-campaign-individual-propertyvaluechanger.md) | Change an individual's **IndividualProperty** value | Y |  |  |  |  |  |
| [RTSSVaccine](parameter-campaign-individual-rtssvaccine.md) | Boost CSP antibody | Y |  |  |  |  |  |
| [ScreeningHousingModification](parameter-campaign-individual-screeninghousingmodification.md) | Modify an individual's house with screens that kill and block vectors | Y | Y |  | Y | Indoor- Die Before/After Feeding | Repelling, killing |
| [SimpleBednet](parameter-campaign-individual-simplebednet.md) | Insecticide Treated Net (ITN) | Y | Y | Wanning Effect Expiration | By Name | Indoor- Die Before/After Feeding | Repelling, blocking, killing |
| [SimpleBoosterVaccine](parameter-campaign-individual-simpleboostervaccine.md) | Not tested with Malaria | Y |  |  |  |  |  |
| [SimpleDiagnostic](parameter-campaign-individual-simplediagnostic.md) | Test if an individual is infected using sensitivity and specificity diagnostics | Y/N |  |  |  |  |  |
| [SimpleHealthSeekingBehavior](parameter-campaign-individual-simplehealthseekingbehavior.md) | Randomly distribute interventions or events to individuals | Y/N |  |  |  |  |  |
| [SimpleHousingModification](parameter-campaign-individual-simplehousingmodification.md) | Block & kill vectors at an individual's house | Y | Y |  | Y | Indoor Die Before/After Feeding | Repelling, killing |
| [SimpleIndividualRepellent](parameter-campaign-individual-simpleindividualrepellent.md) | Block vectors from biting an individual | Y | Y |  |  |  | Repelling |
| [SimpleVaccine](parameter-campaign-individual-simplevaccine.md) | Modify the acquisition, transmission, and mortality effects by distributing a vaccine | Y |  | Wanning Effect Expiration |  |  |  |
| [SpatialRepellentHousingModification](parameter-campaign-individual-spatialrepellenthousingmodification.md) | Block vectors from an individual's house | Y | Y |  | Y |  | Repelling |
| [StandardDiagnostic](parameter-campaign-individual-standarddiagnostic.md) | Test if individuals are infected using sensitivity and specificity diagnostics | Y/N |  |  |  |  |  |
| [UsageDependentBednet](parameter-campaign-individual-usagedependentbednet.md) | Control when individuals use bednets (ITN) | Y | Y | Y | By Name | Indoor Die Before/After Feeding | Repelling, blocking, killing |
