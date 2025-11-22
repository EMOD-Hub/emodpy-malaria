================
ReportAntibodies
================

The antibodies report (ReportAntibodies.csv)  is a csv-formatted report that
provides antibodies data for each qualifying individual on user-determined days of simulation. For example,
individuals between ages 5 and 10 years old, living in node 1, who have the intervention "UsageDependentBednet" and
have the individual property "Risk:LOW" will be documented from day 365 to day 465 of the simulation at 10 day intervals.
The report contains one row per individual per reporting day, with each antibody represented as a separate column.
The values in the report can be either the concentration or capacity of each antibody, depending on user configuration.

Note: This report gets very large, very quickly as well as adding processing time. It is advised to use the
**Reporting_Interval** and other filtering options to limit the size of the report.


Configuration
=============

To generate this report, the following parameters must be configured in the custom_reports.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Reporting_Interval,"float","1.0","1000000.0","1.0","Defines the cadence of the report in days (not timesteps). Data will be recorded every **Reporting_Interval** days starting with the **Start_Day**. This will limit system memory usage and is advised when large output files are expected."
    Contain_Capacity_Data,"boolean","0","1","0","If true (1), the data for each antibody is the capacity of the antibody, otherwise it's the concentration."
    Infected_Only,"boolean","0","1","0","If true (1), only individuals who are currently infected will be included in the report."
    Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
    Filename_Suffix, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
    Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
    End_Day,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
    Node_IDs_Of_Interest,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list.  Empty list implies all nodes."
    Min_Age_Years,"float","0","9.3228e+35","0","Minimum age in years of people to collect data on."
    Max_Age_Years,"float","0","9.3228e+35","9.3228e+35","Maximum age in years of people to collect data on."
    Must_Have_IP_Key_Value, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
    Must_Have_Intervention, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."

.. code-block:: json

    {
        "Reports": [
            {
                "class": "ReportAntibodies",
                "Filename_Suffix": "Node1",
                "Start_Day": 365,
                "End_Day": 465,
                "Node_IDs_Of_Interest": [ 1 ],
                "Min_Age_Years": 5,
                "Max_Age_Years": 10,
                "Must_Have_IP_Key_Value": "Risk:LOW",
                "Must_Have_Intervention": "UsageDependentBednet",
                "Reporting_Interval": 10.0,
                "Contain_Capacity_Data": 1,
                "Infected_Only": 0
            }
        ],
        "Use_Defaults": 1
    }


Stratification columns
----------------------

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    Time, integer, "The day of the simulation that the data was collected."
    NodeID, integer, "The External ID of the node that the data is being collected for."
    IndividualID, integer, The ID of the individual who received the drug.
    Gender, enum, "The gender of the individual. Possible values are M or F."
    AgeYears, integer, The max age in years of the age bin for the individual.
    Infected, boolean, "A true value (1) indicates the individual is infected and a false value (0) indicates the individual is not infected."


Data columns
------------

Note: The report only records people who have been at least exposed to antigens, though they may not currently have measurable antibody levels.
Antibodies that have not been triggered will appear as an empty field in the report.
Antibodies that have been triggered will appear with a numeric value (concentration or capacity) in the report, even if the value is zero.

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    MSP_X, float, "There will be n number of columns named 'MSP_0' to 'MSP_(n-1)' where n is the number of MSP variants as defined by **Falciparum_MSP_Variants** configuration parameter. The value is the concentration or capacity of each MSP antibody variant, depending on the **Contain_Capacity_Data** setting."
    PfEMP1_X, float, "There will be m number of columns named 'PfEMP1_0' to 'PfEMP1_(m-1)' where m is the number of PfEMP1 variants as defined by **Falciparum_PfEMP1_Variants** configuration parameter. The value is the concentration or capacity of each PfEMP1 antibody variant, depending on the **Contain_Capacity_Data** setting."

Example
=======

The following are examples of ReportAntibodiesConcentration.csv and ReportAntibodiesCapacity.csv files.

.. csv-table::
    :header-rows: 1
    :file: ../csv/ReportAntibodiesCapacity.csv

.. csv-table::
    :header-rows: 1
    :file: ../csv/ReportAntibodiesConcentration.csv