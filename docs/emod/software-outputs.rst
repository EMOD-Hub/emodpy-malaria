======================
Output files (reports)
======================

After the simulation finishes, a :term:`reporter` extracts simulation data, aggregates it, and
outputs it to a file (known as an :term:`output report`). Most of the reports are also JSON files,
the most important of which is InsetChart.json. The InsetChart.json file provides simulation-wide
averages of disease prevalence at each :term:`time step`.

After running a simulation, the simulation data is extracted, aggregated, and saved as an
:term:`output report` to the output directory in the working directory. Depending on your
configuration, one or more output reports will be created, each of which summarize different data
from the simulation. Output reports can be in JSON, CSV, or binary file formats. |EMOD_s| also
creates logging or error output files.

The |EMOD_s| functionality that produces an output report is known as a :term:`reporter`. |EMOD_s|
provides several built-in reporters for outputting data from simulations. By default, |EMOD_s| will
always generate the report InsetChart.json, which contains the simulation-wide average disease
prevalence by :term:`time step`. If none of the provided reports generates the output report that
you require, you can create a custom reporter.

.. image:: ../images/intro/output.png
   :scale: 60%

If you want to visualize the data output from an |EMOD_s| simulation, you must use graphing
software to plot the output reports. In addition to output reports, |EMOD_s| will generate error
and logging files to help troubleshoot any issues you may encounter.

Using output reports
====================

By default, the output report InsetChart.json is always produced, which contains per-
time step values accumulated over the simulation in a variety of reporting channels, such as new infections, 
prevalence, and recovered. |EMOD_s| provides several other
built-in reports that you can produce if you enable them in the :term:`configuration file`
with the :doc:`parameter-configuration-output` parameters. Reports are generally in JSON or CSV format.
If none of the built-in output reports provide the data you need, you can use a custom reporter that
plugs in to the |exe_s| as an |module| :term:`dynamic link library (DLL)`. For more information, see
:doc:`software-custom-reporter`.

In order to interpret the output of |EMOD_s| simulations, you will find it useful to parse the output
reports into an analyzable structure. For example, you can use a Python or MATLAB script to create graphs
and charts for analysis.

Convert output to CSV format
----------------------------

Most output reports, including the primary InsetChart report, are in JSON format. If you are using R
for data analysis, you may prefer a CSV report. You can easily convert the output format using
Python post-processing using the icjjson2csv.py_ script provided in the |EMOD_s| GitHub repository.
Provide the path to this script using the ``-P`` argument when you run |exe_s| at the command line.
See :doc:`software-simulation-cli` for more information.


Use Python to plot data
-----------------------

The example below uses the Python package JSON_ to parse the file and the Python package
`matplotlib.pyplot`_ to plot the output. This is a very simple example and not likely the most robust
or elegant. Be sure to set the actual path to your working directory.

.. code-block:: python

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


.. _JSON: http://docs.python.org/library/json.html
.. _matplotlib.pyplot: http://matplotlib.org/api/pyplot_api.html
.. _icjjson2csv.py: https://github.com/InstituteforDiseaseModeling/EMOD/blob/master/Regression/Python/icjjson2csv.py


General reports
===============

Reports for simulation performance, events, demographics, and spatial data.

- :doc:`BinnedReport <software-report-binned>` — Sorts channel data by age bins instead of simulation-wide averages.
- :doc:`DemographicsSummary <software-report-demographic-summary>` — Reports demographic categories like gender ratio and population age groups.
- :doc:`InsetChart <software-report-inset-chart>` — Core report with simulation-wide averages per time step.
- :doc:`PropertyReport <software-report-property>` — Reports counts of individuals by individual property key-value combinations.
- :doc:`ReportEventCounter <software-report-event-counter>` — Counts event occurrences by type during simulation time steps.
- :doc:`ReportEventRecorder <software-report-event-recorder>` — Records individual demographics and health at the time of each event.
- :doc:`ReportHumanMigrationTracking <software-report-human-migration>` — Tracks human travel and migration events during simulations.
- :doc:`ReportInterventionPopAvg <software-report-intervention-population-average>` — Reports intervention usage and efficacy by population fraction.
- :doc:`ReportNodeDemographics <software-report-node-demographics>` — Provides population data stratified by node and age bin.
- :doc:`ReportSimulationStats <software-report-simulation-stats>` — Tracks performance metrics and resource usage per time step.
- :doc:`SpatialReport <software-report-spatial>` — Breaks down channel data by individual nodes in binary files.

.. toctree::
   :hidden:
   :maxdepth: 3
   :titlesonly:

   software-report-binned
   software-report-demographic-summary
   software-report-inset-chart
   software-report-property
   software-report-event-counter
   software-report-event-recorder
   software-report-human-migration
   software-report-intervention-population-average
   software-report-node-demographics
   software-report-simulation-stats
   software-report-spatial


Vector reports
==============

Reports for vector biology and mosquito population dynamics.

- :doc:`ReportVectorGenetics <software-report-vector-genetics>` — Reports vector genome and allele combinations by state.
- :doc:`ReportVectorMigration <software-report-vector-migration>` — Provides detailed information on vector migration locations.
- :doc:`ReportVectorStats <software-report-vector-stats>` — Reports detailed vector life-cycle data stratified by time, node, and species.
- :doc:`VectorHabitatReport <software-report-vector-habitat>` — Reports habitat data for vector species developmental stages.
- :doc:`VectorSpeciesReport <software-report-vector-species>` — Sorts vector data into bins by species with adult vector counts.

.. toctree::
   :hidden:
   :maxdepth: 3
   :titlesonly:

   software-report-vector-genetics
   software-report-vector-migration
   software-report-vector-stats
   software-report-vector-habitat
   software-report-vector-species


Malaria — Population and epidemiology
======================================

Reports for malaria disease burden, prevalence, and population-level statistics.

- :doc:`MalariaSummaryReport <software-report-malaria-summary>` — Provides a population-level malaria summary grouped by age and parasitemia bins.
- :doc:`ReportMalariaFiltered <software-report-filtered-malaria>` — Filtered InsetChart with options for data selection by time, node, or individual property.
- :doc:`ReportNodeDemographicsMalaria <software-report-malaria-node-demographics>` — Extends node demographics with malaria parasite counts.
- :doc:`SpatialReportMalariaFiltered <software-report-malaria-spatial>` — Spatial malaria information with filtering and custom reporting intervals.
- :doc:`SqlReportMalaria <software-report-sql-malaria>` — Outputs generic epidemiological data in SQLite relational database format.
- :doc:`SqlReportMalaria <software-report-sql-malaria>` — Outputs malaria epidemiological data in SQLite relational database format.

.. toctree::
   :hidden:
   :maxdepth: 3
   :titlesonly:

   software-report-malaria-summary
   software-report-filtered-malaria
   software-report-malaria-node-demographics
   software-report-malaria-spatial
   software-report-sql
   software-report-sql-malaria


Malaria — Intra-host
=====================

Reports for within-host infection dynamics, drug status, and individual patient data.

- :doc:`MalariaImmunityReport <software-report-malaria-immunity>` — Reports antibody statistics for MSP and PfEMP1 by age bins.
- :doc:`MalariaPatientJSONReport <software-report-malaria-patient>` — Reports medical data for each individual on each day.
- :doc:`MalariaSurveyJSONAnalyzer <software-report-malaria-survey>` — Reports individual details for each event during the reporting interval.
- :doc:`ReportAntibodies <software-report-antibodies>` — Tracks antibody concentration or capacity data per individual per day.
- :doc:`ReportDrugStatus <software-report-drug-status>` — Reports drug status for individuals who have taken or are awaiting treatment.
- :doc:`ReportInfectionDuration <software-report-infection-duration>` — Records the duration of each cleared infection along with individual demographics.
- :doc:`ReportMalariaFilteredIntraHost <software-report-malaria-filtered-intra-host>` — Reports within-host disease dynamics with a focused set of intra-host channels.

.. toctree::
   :hidden:
   :maxdepth: 3
   :titlesonly:

   software-report-malaria-immunity
   software-report-malaria-patient
   software-report-malaria-summary
   software-report-malaria-survey
   software-report-antibodies
   software-report-drug-status
   software-report-infection-duration
   software-report-malaria-filtered-intra-host


Parasite genetics (FPG)
========================

Reports for parasite genome tracking and full parasite genetics simulations.

- :doc:`ReportFpgNewInfections <software-report-fpg-new-infections>` — Tracks detailed new human infections with parasite genetics data.
- :doc:`ReportFpgOutputForObservationalModel <software-report-fpg-output-observational-model>` — Extract data for the FPGObservational model.
- :doc:`ReportNodeDemographicsMalariaGenetics <software-report-malaria-node-demographics-genetics>` — Adds specific genetic barcode infection counts to node demographics.
- :doc:`ReportSimpleMalariaTransmission <software-report-simple-malaria-transmission>` — Tracks who transmitted malaria to whom during co-transmission events.
- :doc:`ReportVectorStatsMalariaGenetics <software-report-vector-stats-malaria-genetics>` — Reports vector life-cycle data with genetic barcode information.
- :doc:`SqlReportMalariaGenetics <software-report-sql-malaria-genetics>` — Outputs malaria epidemiological and genetics data in SQLite relational database format.

.. toctree::
   :hidden:
   :maxdepth: 3
   :titlesonly:

   software-report-fpg-new-infections
   software-report-fpg-output-observational-model
   software-report-malaria-node-demographics-genetics
   software-report-simple-malaria-transmission
   software-report-vector-stats-malaria-genetics
   software-report-sql-malaria-genetics


Other
=====

- :doc:`Custom reporters <software-custom-reporter>` — Describes how to build and load custom reporters that extract simulation data not covered by built-in reports.
- :doc:`Error and logging files <software-error-logging>` — Describes the error and logging files generated when running a simulation.

.. toctree::
   :hidden:
   :maxdepth: 3
   :titlesonly:

   software-custom-reporter
   software-error-logging