======================
ReportFpgNewInfections
======================


The full parasite genetics new infections report (ReportFpgNewInfections.csv) provides very detailed information on
new human infections for simulations where **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.
When **Report_Crossover_Data_Instead** is set to true, it provides less detailed information on the new infections
and includes GenomeCrossoverLocations data column that provides a list of crossovers that created this new infection's
genome.



Configuration
=============

To generate this report, configure the following parameters in the custom_report.json file:

.. csv-table::
    :header: Parameter name, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Filename_Suffix, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
    Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
    End_Day,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
    Node_IDs_Of_Interest,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list.  Empty list implies all nodes."
    Min_Age_Years,"float","0","9.3228e+35","0","Minimum age in years of people to collect data on."
    Max_Age_Years,"float","0","9.3228e+35","9.3228e+35","Maximum age in years of people to collect data on."
    Must_Have_IP_Key_Value, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
    Must_Have_Intervention, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
    Report_Crossover_Data_Instead, boolean, NA, NA, False, "If true (1), instead of reporting new infections in detail, the report will contain basic new infection information with the crossover locations that created this infection's genome."


.. code-block:: json

    {
        "Reports": [
            {
                "Start_Day": 500,
                "End_Day": 1000,
                "Filename_Suffix":"Crossovers",
                "Node_IDs_Of_Interest": [],
                "Min_Age_Years": 0,
                "Max_Age_Years": 1000,
                "Must_Have_IP_Key_Value": "",
                "Must_Have_Intervention": "",
                "Report_Crossover_Data_Instead": 1,
                "class": "ReportFpgNewInfections"
            },
        ],
        "Use_Defaults": 1
    }


Output data with Report_Crossover_Data_Instead = 0
==================================================

Each row of the report is one new human infection.
The report contains the following stratification columns:

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    SporozoiteToHuman_Time, float, The day of the simulation this infection happened.
    SporozoiteToHuman_NodeID, integer, The ID of the node in which this infection happened.
    SporozoiteToHuman_VectorID, integer, The ID of the vector from which the human got this infection.
    SporozoiteToHuman_BiteID, integer, The the ID of the bite from which the human got this infection.
    SporozoiteToHuman_HumanID, integer, The ID of the human that got this infection.
    SporozoiteToHuman_NewInfectionID, integer, The ID of this infection.
    SporozoiteToHuman_NewGenomeID, integer, The genome ID of this infection.
    HomeNodeID, integer, The home node ID of the human (the node in which they started the simulation) who received this new infection.
    GametocyteToVector_Time, float, The day the vector acquired gametocytes (bit an infectious human) that eventually became this new infection.
    GametocyteToVector_NodeID, integer, The ID of the node in which the vector acquired gametocytes.
    GametocyteToVector_VectorID, integer, The ID of the vector from which the human got this infection.
    GametocyteToVector_BiteID, integer, The ID of the bite during which the vector acquired gametocytes that became this new infection.
    GametocyteToVector_HumanID, integer, The ID of the human from whom the vector acquired gametocytes that became this new infection.
    FemaleGametocyteToVector_InfectionID, integer, The ID of the vector to human infection that generated female gametocytes that were acquired by the vector that became this infection.
    FemaleGametocyteToVector_GenomeID, integer, The genome ID of the female gametocytes that were acquired by the vector that became this infection.
    MaleGametocyteToVector_InfectionID, integer, The ID of the vector to human infection that generated male gametocytes that were acquired by the vector that became this infection.
    MaleGametocyteToVector_GenomeID, integer, The genome ID of the male gametocytes that were acquired by the vector that became this infection.


Output data with Report_Crossover_Data_Instead = 1
==================================================

Each row of the report is one new human infection. This is the output when **Report_Crossover_Data_Instead** is set to true (1).
The report contains the following stratification columns:

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    SporozoiteToHuman_Time, float, The day of the simulation this infection happened.
    SporozoiteToHuman_NewInfectionID, integer, The ID of this infection.
    SporozoiteToHuman_NewGenomeID, integer, The genome ID of this infection.
    FemaleGametocyteToVector_InfectionID, integer, The ID of the vector to human infection that generated female gametocytes that were acquired by the vector that became this infection.
    FemaleGametocyteToVector_GenomeID, integer, The genome ID of the female gametocytes that were acquired by the vector that became this infection.
    MaleGametocyteToVector_InfectionID, integer, The ID of the vector to human infection that generated male gametocytes that were acquired by the vector that became this infection.
    MaleGametocyteToVector_GenomeID, integer, The genome ID of the male gametocytes that were acquired by the vector that became this infection.
    GenomeCrossoverLocations, "array of integers", The genome locations of crossovers that happened during the recombination to create the genome of this infection.


Examples
========

The following is an example of ReportFpgNewInfections.csv with Report_Crossover_Data_Instead = 0

.. csv-table::
    :header: SporozoiteToHuman_Time, SporozoiteToHuman_NodeID,	SporozoiteToHuman_VectorID,	SporozoiteToHuman_BiteID,	SporozoiteToHuman_HumanID,	SporozoiteToHuman_NewInfectionID,	SporozoiteToHuman_NewGenomeID,	HomeNodeID,	GametocyteToVector_Time,	GametocyteToVector_NodeID,	GametocyteToVector_VectorID	GametocyteToVector_BiteID,	GametocyteToVector_HumanID,	FemaleGametocyteToVector_InfectionID,	FemaleGametocyteToVector_GenomeID,	MaleGametocyteToVector_InfectionID, MaleGametocyteToVector_GenomeID
    :widths: 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8
    :file: ../csv/ReportFpgNewInfections.csv


The following is an example of ReportFpgNewInfections.csv with Report_Crossover_Data_Instead = 1

.. csv-table::
    :header: SporozoiteToHuman_Time, SporozoiteToHuman_NewInfectionID, SporozoiteToHuman_NewGenomeID, FemaleGametocyteToVector_InfectionID, FemaleGametocyteToVector_GenomeID,	MaleGametocyteToVector_InfectionID,	MaleGametocyteToVector_GenomeID, GenomeCrossoverLocations
    :widths: 8, 8, 8, 8, 8, 8, 8, 8
    :file: ../csv/ReportFpgNewInfections_Crossovers.csv




