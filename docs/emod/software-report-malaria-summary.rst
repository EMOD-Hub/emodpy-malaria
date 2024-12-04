====================
MalariaSummaryReport
====================

The malaria summary report (MalariaSummaryReport.json) is a JSON-formatted report that provides a
population-level summary of malaria data grouped into different bins such as age, parasitemia, and
infectiousness.



Configuration
=============

To generate this report, the following parameters must be configured in the custom_reports.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Filename_Suffix**, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
    **Start_Day**,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
    **End_Day**,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
    **Node_IDs_Of_Interest**,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list.  Empty list implies all nodes."
    **Must_Have_IP_Key_Value**, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
    **Must_Have_Intervention**, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
    **Reporting_Interval**, integer, 1, 1000000, 1000000, "Defines the cadence of the report by specifying how many time steps to collect data before writing to the file. This will limit system memory usage and is advised when large output files are expected."
    **Max_Number_Reports**, integer, 0, 1000000, 1, The maximum number of report output files that will be produced for a given campaign per simulation.
    **Pretty_Format**, boolean, 0, 1, 0, "True (1) sets pretty JSON formatting. The default, false (0), saves space."
    **Age_Bins**, array of floats, 0, 125, "[10,20,30,40,50,60,70,80,90,100,1000]", "The age bins to aggregate within and report. Data must be in ascending order."
    **Parasitemia_Bins**, float, -3.40E+38, 3.40E+38, "[50,500,5000,50000,FLT_MAX]", "Parasitemia Bins to aggregate within and report.  A value greater than or equal to zero in the first bin indicates that the uninfected people should be added to this bin.  The values must be in ascending order."
    **Infectiousness_Bins**, float, -3.40E+38, 3.40E+38, "[20,40,60,80,100]", Infectiousness bins to aggregate within and report.
    **Individual_Property_Filter**, string, NA, NA, (empty string), "The individual 'property:value' to filter on. The default of an empty string means the report is not filtered. For example: 'Risk:High'."
    **Use_True_Density_Vs_Threshold**, boolean, 0, 1, 0, "If set to true, the true parasite/gametocyte density will be used instead of the microscopy measurement for the following channels: 'PfPR_2to10', 'PfPR by Age Bin', 'Pf Gametocyte Prevalence by Age Bin', and 'Mean Log Parasite Density by Age Bin'.  The true density will be compared to thresholds: config.Report_Detection_Threshold_True_Parasite_Density and MalariaSummaryReport.Detection_Threshold_True_Gametocyte_Density.  If false, then BLOOD_SMEAR_PARASITES/BLOOD_SMEAR_GAMETOCYTES measurements are used (have uncertainty in the measurement).  The parasite measurement is compared against a threshold of zero and the gametocyte measurement a threshold of 0.02."
    **Detection_Threshold_True_Gametocyte_Density**, float, 0, 3.40E+38, 0, "Used when 'Use_True_Density_Vs_Threshold' is true.  The true gametocyte density is compared against this threshold.  It impacts the 'Pf Gametocyte Prevalence by Age Bin' channel."


.. code-block:: json

    {
        "Reports": [
            {
                "class": "MalariaSummaryReport",
                "Filename_Suffix": "Node1",
                "Start_Day": 365,
                "End_Day": 465,
                "Use_True_Density_Vs_Threshold" : 0,
                "Node_IDs_Of_Interest": [ 1 ],
                "Must_Have_IP_Key_Value": "Risk:LOW",
                "Must_Have_Intervention": "UsageDependentBednet"
                "Reporting_Interval": 10,
                "Max_Number_Reports": 1,
                "Pretty_Format": 1,
                "Age_Bins": [
                    10,
                    20,
                    30,
                    40,
                    50,
                    60,
                    70,
                    80,
                    90,
                    100,
                    125
                ],
                "Parasitemia_Bins": [
                    50,
                    500,
                    5000,
                    50000
                ],
                "Infectiousness_Bins": [
                    20,
                    40,
                    60,
                    80,
                    100
                ],
                "Individual_Property_Filter": "Risk:High"
            }
        ],
        "Use_Defaults": 1
    }




Output file data
================

These output files may be very large. They contain several sections of data:

* Metadata
* DataByTime
* DataByTimeAndAgeBins
* DataByTimeAndPfPRBinsAndAgeBins
* DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins



Metadata
--------

This section contains the group of parameters used to configure the report, and includes the following
data channels:

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    **Start_Day**, integer, The first day that the first interval started.
    **Reporting_Interval**, integer, The number of days to accumulate data.
    **Age Bins**, array of integers, "The max age in years per bin, listed in ascending order.  Note that by using a large value for the last bin, it will  collect all remaining people."
    **Parasitemia Bins**, array of integers, "The max parasite density in infected red blood cells per microliter per bin, listed in ascending order."
    **Gametocytemia Bins**, array of integers, "The max gametocyte density in infected red blood cells per microliter per bin, listed in ascending order."
    **Infectiousness Bins**, array of integers, "The max percent infectiousness of each bin, listed in ascending order."



DataByTime
----------

This section contains a group of statistics where there is just one entry for each reporting interval.
The following statistics are collected:

.. csv-table::
    :header: Parameter, Description
    :widths: 8, 20

    Time Of Report, "Each entry is the final day of the reporting interval, in days."
    Annual EIR, "The average Entomological Inoculation Rate (EIR) per year over the reporting interval."
    PfPR_2to10, "The fraction of individuals whose age is 2 < age < 10 that would have been detected with the BLOOD_SMEAR_PARASITES diagnostic type of MalariaDiagnostic where the sensitivity is **Report_Parasites_Smear_Sensitivity** and the detection threshold is zero.  Please note that his measurement includes some random noise.  If **Use_True_Density_Vs_Threshold** is set to true (1), then true parasite density is compared against the **Report_Detection_Threshold_True_Parasite_Density** value."
    No Infection Streak, The maximum number of days without an infection during the interval.
    Fraction Days Under 1pct Infected, The percentage of days during the interval in which the percentage of infected individuals was less than 1%.


DataByTimeAndAgeBins
--------------------

This section contains statistics in two-dimensional arrays by Time (the reporting interval) and
Age Bin.

.. csv-table::
    :header: Parameter, Description
    :widths: 8, 20

    PfPR by Age Bin, "The fraction of individuals in this age bin that would have been detected using the BLOOD_SMEAR_PARASITES diagnostic type of the MalariaDiagnostic intervention where the sensitivity is **Report_Parasites_Smear_Sensitivity** and the detection threshold is zero.  Please note that his measurement includes some random noise.  If **Use_True_Density_Vs_Threshold** is set to true (1), then true parasite density is compared against the **Report_Detection_Threshold_True_Parasite_Density** value."    
    pf Gametocyte Prevalence by Age Bin, "The fraction of individuals in this age bin that would have been detected using the BLOOD_SMEAR_GAMETOCYTES diagnostic type of the MalariaDiagnostic intervention where the sensitivity is **Report_Gametocyte_Smear_Sensitivity** and the detection threshold is 0.02.  Please note that his measurement includes some random noise.  If **Use_True_Density_Vs_Threshold** is set to true (1), then true gametocyte density is compared against the **Detection_Threshold_True_Gametocyte_Density** value."    
    Mean Log Parasite Density by Age Bin, "The average Log10 parasite density of the population for that age bin based on the count of parasites using the BLOOD_SMEAR_PARASITES diagnostic type of MalariaDiagnostic where the sensitivity is **Report_Parasites_Smear_Sensitivity**.  Please note that his measurement includes some random noise.  If **Use_True_Density_Vs_Threshold** is set to true (1), then Log10 is taken of the true parasite density.
    New Infections by Age Bin, "The number of new infections during the reporting interval for each age bin."
    Annual Clinical Incidence by Age Bin, "The number of new clinical symptoms per person per year.  This channel is controlled by the **Clinical_Fever_Threshold_Low** and **Clinical_Fever_Threshold_High** parameters.  The amount that an individual’s fever is above normal must be greater than both of these values to be considered clinical.  This can also be influenced by the **Min_Days_Between_Clinical_Incidents** parameter."
    Annual Severe Incidence by Age Bin, "The number of new severe symptoms per person per year.  An individual is considered to be a severe case if the combined probability of anemia, parasite density, and fever is greater than a uniform random number.  This combined probability is the combination of sigmoid using the following parameters: **Anemia_Severe_Threshold** and **Anemia_Severe_Inverse_Width**, **Parasite_Severe_Threshold** and **Parasite_Severe_Inverse_Width**, **Fever_Severe_Threshold** and **Fever_Severe_Inverse_Width**."
    Average Population by Age Bin, The average population of the people in the given age bin over the reporting internal/period.
    Annual Severe Incidence by Anemia by Age Bin, "The number of severe incidences by anemia per person per year.  The sum of the people who have severe symptoms of type: anemia during each timestep during the reporting interval multiplied by 365 and divided by the sum of the people in the age bin during each timestep during the reporting interval.  Impacted by **Anemia_Severe_Threshold** and **Anemia_Severe_Inverse_Width**."
    Annual Severe Incidence by Parasites by Age Bin, "The number of severe incidences by parasites per person per year.  The sum of the people who have severe symptoms of type: parasites during each timestep during the reporting interval multiplied by 365 and divided by the sum of the people in the age bin during each time step during the reporting interval.  Impacted by **Parasite_Severe_Threshold** and **Parasite_Severe_Inverse_Width**."
    Annual Severe Incidence by Fever by Age Bin, "The number of severe incidences by fever per person per year.  The sum of the people who have severe symptoms of type fever during each timestep during the reporting interval multiplied by 365 and divided by the sum of the people in the age bin during each time step during the reporting interval.  Impacted by **Fever_Severe_Threshold** and **Fever_Severe_Inverse_Width**."
    Annual Severe Anemia by Age Bin, "The number of times a person’s hemoglobin count is less than 5 per person per year.  The sum of the people whose hemoglobin is < 5 during each timestep during the reporting interval multiplied by 365 and divided by the sum of the people in the age bin during each time step during the reporting interval."
    Annual Moderate Anemia by Age Bin, "The number of times a person’s hemoglobin count is less than 8 per person per year.  This includes everyone who was Severe.  The sum of the people whose hemoglobin is < 8 during each timestep during the reporting interval multiplied by 365 and divided by the sum of the people in the age bin during each time step during the reporting interval."
    Annual Mild Anemia by Age Bin, "The number of times a person’s hemoglobin count is less than 11 per person per year.  This includes everyone who was Severe and Moderate.  The sum of the people whose hemoglobin is < 11 during each timestep during the reporting interval multiplied by 365 and divided by the sum of the people in the age bin during each time step during the reporting interval."


DataByTimeAndPfPRBinsAndAgeBins
-------------------------------

This section contains statistics in three-dimensional arrays: Time (the reporting interval),
Parasitemia Bins, and Age Bins.

.. csv-table::
    :header: Parameter, Description
    :widths: 8, 20

    PfPR by Parasitemia and Age Bin, "The fraction of individuals whose parasite density and age fall into this bin. The sum of the people whose true parasite density in the PfPRBin and age bin divided by the total number of people in the age bin.  Please note that people with zero parasitemia (i.e. only gametocytes) are counted in the bin that includes zero."
    PfPR by Gametocytemia and Age Bin, "The fraction of individuals whose gametocyte density and age fall into this gametocyte bin.  Please note that people with zero gametocytes are counted in the bin that includes zero."
    Smeared PfPR by Parasitemia and Age Bin, "The fraction of individuals in this age bin whose true parasite density when smeared by CountPositiveSlideFields falls into this parasitemia bin."
    Smeared PfPR by Gametocytemia and Age Bin, "The fraction of individuals in this age bin whose true gametocyte density when smeared by CountPositiveSlideFields falls into this gametocyte bin."
    Smeared True PfPR by Parasitemia and Age Bin, "The fraction of individuals in this age bin whose true parasite density when smeared by NASBADensityWithUncertainty falls into this parasitemia bin."
    Smeared True PfPR by Gametocytemia and Age Bin, "The fraction of individuals in this age bin whose true gametocyte density when smeared by  NASBADensityWithUncertainty falls into this parasitemia bin."


DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins
----------------------------------------------------

This section contains statistics in four-dimensional arrays: Time (the reporting interval),
Infectiousness, Parasitemia Bins, and Age Bins.


.. csv-table::
    :header: Parameter, Description
    :widths: 8, 20

    Infectiousness by Gametocytemia and Age Bin, "The fraction of individuals whose infectiousness, gametocyte density, and age fall into these bins."
    Age scaled Infectiousness by Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is scaled by their age-dependent Surface Area Biting, gametocyte density and age fall into these bins."
    Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age fall into these bins."
    Smeared Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is smeared by BinomialInfectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age falls into these bins."
    Age scaled Smeared Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is first scaled by Surface Area Biting and then smeared by BinomialInfectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age falls into these bins."



Example
=======


The following is a sample of a MalariaSummaryReport.json file.

.. literalinclude:: ../json/report-malaria-summary.json
   :language: json

