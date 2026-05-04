# Output files (reports)


After the simulation finishes, a *reporter* extracts simulation data, aggregates it, and
outputs it to a file (known as an *output report*). Most of the reports are also JSON files,
the most important of which is InsetChart.json. The InsetChart.json file provides simulation-wide
averages of disease prevalence at each *time step*.

After running a simulation, the simulation data is extracted, aggregated, and saved as an
*output report* to the output directory in the working directory. Depending on your
configuration, one or more output reports will be created, each of which summarize different data
from the simulation. Output reports can be in JSON, CSV, or binary file formats. EMOD also
creates logging or error output files.

The EMOD functionality that produces an output report is known as a *reporter*. EMOD
provides several built-in reporters for outputting data from simulations. By default, EMOD will
always generate the report InsetChart.json, which contains the simulation-wide average disease
prevalence by *time step*. If none of the provided reports generates the output report that
you require, you can create a custom reporter.

![output.png](../figures/intro/output.png)

If you want to visualize the data output from an EMOD simulation, you must use graphing
software to plot the output reports. In addition to output reports, EMOD will generate error
and logging files to help troubleshoot any issues you may encounter.

## Using output reports


By default, the output report InsetChart.json is always produced, which contains per-
time step values accumulated over the simulation in a variety of reporting channels, such as new infections, 
prevalence, and recovered. EMOD provides several other
built-in reports that you can produce if you enable them in the *configuration file*
with the [parameter-configuration-output](parameter-configuration-output.md) parameters. Reports are generally in JSON or CSV format.

In order to interpret the output of EMOD simulations, you will find it useful to parse the output
reports into an analyzable structure. For example, you can use a Python or R script to create graphs
and charts for analysis.

### Use Python to plot data


The example below uses the Python package JSON_ to parse the file and the Python package
[matplotlib.pyplot][matplotlib-pyplot] to plot the output. This is a very simple example and not likely the most robust
or elegant. Be sure to set the actual path to your working directory.

```python
import os
import json
import matplotlib.pyplot as plt

# open and parse InsetChart.json
ic_json = json.loads( open( os.path.join( WorkingDirectoryLocation, "output", "InsetChart.json" ) ).read() )
ic_json_allchannels = ic_json["Channels"]
ic_json_birthdata = ic_json["Channels"]["Births"]

# plot "Births" channel by time step
plt.plot( ic_json_birthdata[  "Data"  ], 'b-' )
plt.title( "Births" )
plt.show()
```



## General reports


Reports for simulation performance, events, demographics, and spatial data.

- [BinnedReport](software-report-binned.md) — Sorts channel data by age bins instead of simulation-wide averages.
- [DemographicsSummary](software-report-demographic-summary.md) — Reports demographic categories like gender ratio and population age groups.
- [InsetChart](software-report-inset-chart.md) — Core report with simulation-wide averages per time step.
- [PropertyReport](software-report-property.md) — Reports counts of individuals by individual property key-value combinations.
- [ReportEventCounter](software-report-event-counter.md) — Counts event occurrences by type during simulation time steps.
- [ReportEventRecorder](software-report-event-recorder.md) — Records individual demographics and health at the time of each event.
- [ReportHumanMigrationTracking](software-report-human-migration.md) — Tracks human travel and migration events during simulations.
- [ReportInterventionPopAvg](software-report-intervention-population-average.md) — Reports intervention usage and efficacy by population fraction.
- [ReportNodeDemographics](software-report-node-demographics.md) — Provides population data stratified by node and age bin.
- [ReportSimulationStats](software-report-simulation-stats.md) — Tracks performance metrics and resource usage per time step.
- [SpatialReport](software-report-spatial.md) — Breaks down channel data by individual nodes in binary files.

## Vector reports


Reports for vector biology and mosquito population dynamics.

- [ReportMicrosporidia](software-report-microsporidia.md) — Tracks vector population counts by species and microsporidia strain across all life stages.
- [ReportVectorGenetics](software-report-vector-genetics.md) — Reports vector genome and allele combinations by state.
- [ReportVectorMigration](software-report-vector-migration.md) — Provides detailed information on vector migration locations.
- [ReportVectorStats](software-report-vector-stats.md) — Reports detailed vector life-cycle data stratified by time, node, and species.
- [VectorHabitatReport](software-report-vector-habitat.md) — Reports habitat data for vector species developmental stages.
- [VectorSpeciesReport](software-report-vector-species.md) — Sorts vector data into bins by species with adult vector counts.

## Malaria — Population and epidemiology


Reports for malaria disease burden, prevalence, and population-level statistics.

- [MalariaSummaryReport](software-report-malaria-summary.md) — Provides a population-level malaria summary grouped by age and parasitemia bins.
- [ReportMalariaFiltered](software-report-filtered-malaria.md) — Filtered InsetChart with options for data selection by time, node, or individual property.
- [ReportNodeDemographicsMalaria](software-report-malaria-node-demographics.md) — Extends node demographics with malaria parasite counts.
- [SpatialReportMalariaFiltered](software-report-malaria-spatial.md) — Spatial malaria information with filtering and custom reporting intervals.
- [SqlReport](software-report-sql.md) — Outputs individual-level epidemiological data in SQLite relational database format.
- [SqlReportMalaria](software-report-sql-malaria.md) — Outputs malaria epidemiological data in SQLite relational database format.

## Malaria — Intra-host


Reports for within-host infection dynamics, drug status, and individual patient data.

- [MalariaImmunityReport](software-report-malaria-immunity.md) — Reports antibody statistics for MSP and PfEMP1 by age bins.
- [MalariaPatientJSONReport](software-report-malaria-patient.md) — Reports medical data for each individual on each day.
- [MalariaSurveyJSONAnalyzer](software-report-malaria-survey.md) — Reports individual details for each event during the reporting interval.
- [ReportAntibodies](software-report-antibodies.md) — Tracks antibody concentration or capacity data per individual per day.
- [ReportDrugStatus](software-report-drug-status.md) — Reports drug status for individuals who have taken or are awaiting treatment.
- [ReportInfectionDuration](software-report-infection-duration.md) — Records the duration of each cleared infection along with individual demographics.
- [ReportInfectionStatsMalaria](software-report-infection-stats-malaria.md) — Reports per-infection parasite burden (hepatocytes, IRBCs, gametocytes) for every active infection at each reporting interval.
- [ReportMalariaFilteredIntraHost](software-report-malaria-filtered-intra-host.md) — Reports within-host disease dynamics with a focused set of intra-host channels.

## Malaria - Parasite genetics (FPG)


Reports for parasite genome tracking and full parasite genetics simulations.

- [ReportFpgNewInfections](software-report-fpg-new-infections.md) — Tracks detailed new human infections with parasite genetics data.
- [ReportFpgOutputForObservationalModel](software-report-fpg-output-observational-model.md) — Extracts genetic and epidemiological data on the filtered infected population for use with the FPGObservationalModel post-processing tool.
- [ReportNodeDemographicsMalariaGenetics](software-report-malaria-node-demographics-genetics.md) — Adds specific genetic barcode infection counts to node demographics.
- [ReportSimpleMalariaTransmission](software-report-simple-malaria-transmission.md) — Tracks who transmitted malaria to whom; requires `MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION` and is typically used as input to the GenEpi model.
- [ReportVectorStatsMalariaGenetics](software-report-vector-stats-malaria-genetics.md) — Reports vector life-cycle data with genetic barcode information.
- [SqlReportMalariaGenetics](software-report-sql-malaria-genetics.md) — Outputs malaria epidemiological and genetics data in SQLite relational database format.

## Other


- [Error and logging files](software-error-logging.md) — Describes the error and logging files generated when running a simulation.
- **stdout.txt** — Contains the logging output written by EMOD to standard output during a simulation run.
- **stderr.txt** — Contains error messages written by EMOD or Python to standard error during a simulation run.
- [Troubleshooting](troubleshooting.md) — Lists common exceptions and errors encountered when running simulations and explains how to resolve them.
