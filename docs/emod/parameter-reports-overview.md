# Reports and other output

After the simulation finishes, a *reporter* extracts simulation data, aggregates it, and
outputs it to a file (known as an *output report*). You can use any of the reporters below
to get different information about your simulation, from memory usage to infection counts
to parasite genetics.

## General reports

| Report | Description |
|--------|-------------|
| [InsetChart](software-report-inset-chart.md) | Automatically generated; simulation-wide averages of key channels at each time step. |
| [DemographicsSummary](software-report-demographic-summary.md) | Demographic channel data aggregated across the simulation; enabled together with BinnedReport. |
| [BinnedReport](software-report-binned.md) | Channel data stratified by age bins instead of simulation-wide averages; enabled together with DemographicsSummary. |
| [PropertyReport](software-report-property.md) | Counts of individuals broken down by individual property key-value combinations. |
| [ReportEventCounter](software-report-event-counter.md) | Counts how many times each event occurs per time step. |
| [ReportEventRecorder](software-report-event-recorder.md) | Records individual demographics and health at the time of each event. |
| [ReportHumanMigrationTracking](software-report-human-migration.md) | Tracks human travel and migration events during simulations. |
| [ReportInterventionPopAvg](software-report-intervention-population-average.md) | Reports intervention usage and efficacy by population fraction. |
| [ReportNodeDemographics](software-report-node-demographics.md) | Node-level demographic snapshot at each time step. |
| [ReportSimulationStats](software-report-simulation-stats.md) | Tracks performance, memory usage, and simulation object counts at each time step. |
| [SpatialReport](software-report-spatial.md) | Channel data broken down per geographic node in binary files. |

## Vector reports

| Report | Description |
|--------|-------------|
| [ReportMicrosporidia](software-report-microsporidia.md) | Tracks vector population counts by species and microsporidia strain across all life stages. |
| [ReportVectorGenetics](software-report-vector-genetics.md) | Reports vector genome and allele combinations by state. |
| [ReportVectorMigration](software-report-vector-migration.md) | Provides detailed information on vector migration locations. |
| [ReportVectorStats](software-report-vector-stats.md) | Detailed vector life-cycle data stratified by time, node, and species. |
| [VectorHabitatReport](software-report-vector-habitat.md) | Reports habitat data for vector species developmental stages. |
| [VectorSpeciesReport](software-report-vector-species.md) | Sorts vector data into bins by species with adult vector counts. |

## Malaria — Population and epidemiology

| Report | Description |
|--------|-------------|
| [MalariaSummaryReport](software-report-malaria-summary.md) | Population-level malaria summary grouped by age and parasitemia bins. |
| [ReportMalariaFiltered](software-report-filtered-malaria.md) | Filtered InsetChart with options for data selection by time, node, or individual property. |
| [ReportNodeDemographicsMalaria](software-report-malaria-node-demographics.md) | Extends node demographics with malaria parasite counts. |
| [SpatialReportMalariaFiltered](software-report-malaria-spatial.md) | Spatial malaria information with filtering and custom reporting intervals. |
| [SqlReport](software-report-sql.md) | Outputs individual-level epidemiological data to a SQLite relational database. |
| [SqlReportMalaria](software-report-sql-malaria.md) | Outputs malaria epidemiological data to a SQLite relational database. |

## Malaria — Intra-host

| Report | Description |
|--------|-------------|
| [MalariaImmunityReport](software-report-malaria-immunity.md) | Reports antibody statistics for MSP and PfEMP1 by age bins. |
| [MalariaPatientJSONReport](software-report-malaria-patient.md) | Reports medical data for each individual on each day. |
| [MalariaSurveyJSONAnalyzer](software-report-malaria-survey.md) | Reports individual details for each event during the reporting interval. |
| [ReportAntibodies](software-report-antibodies.md) | Tracks antibody concentration or capacity data per individual per day. |
| [ReportDrugStatus](software-report-drug-status.md) | Reports drug status for individuals who have taken or are awaiting treatment. |
| [ReportInfectionDuration](software-report-infection-duration.md) | Records the duration of each cleared infection along with individual demographics. |
| [ReportInfectionStatsMalaria](software-report-infection-stats-malaria.md) | Reports per-infection parasite burden (hepatocytes, IRBCs, gametocytes) at each reporting interval. |
| [ReportMalariaFilteredIntraHost](software-report-malaria-filtered-intra-host.md) | Reports within-host disease dynamics with a focused set of intra-host channels. |

## Malaria — Parasite genetics (FPG)

| Report | Description |
|--------|-------------|
| [ReportFpgNewInfections](software-report-fpg-new-infections.md) | Tracks detailed new human infections with parasite genetics data. |
| [ReportFpgOutputForObservationalModel](software-report-fpg-output-observational-model.md) | Extracts genetic and epidemiological data on the filtered infected population for use with the FPGObservationalModel post-processing tool. |
| [ReportNodeDemographicsMalariaGenetics](software-report-malaria-node-demographics-genetics.md) | Adds specific genetic barcode infection counts to node demographics. |
| [ReportSimpleMalariaTransmission](software-report-simple-malaria-transmission.md) | Tracks who transmitted malaria to whom; requires `MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION`. |
| [ReportVectorStatsMalariaGenetics](software-report-vector-stats-malaria-genetics.md) | Reports vector life-cycle data with genetic barcode information. |
| [SqlReportMalariaGenetics](software-report-sql-malaria-genetics.md) | Outputs malaria epidemiological and genetics data to a SQLite relational database. |

## Other

| File | Description |
|------|-------------|
| [Error and logging files](software-error-logging.md) | Error output and logging information generated during a simulation run. |
| **stdout.txt** | Contains the logging output written by EMOD to standard output during a simulation run. |
| **stderr.txt** | Contains error messages written by EMOD or Python to standard error during a simulation run. |
| [Troubleshooting](troubleshooting.md) | Help resolving common simulation errors. |
