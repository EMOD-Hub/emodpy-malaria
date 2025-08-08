====================
MalariaSummaryReport
====================

The malaria summary report (MalariaSummaryReport.json) is a JSON-formatted report that provides a
population-level summary of malaria data grouped into different bins such as age, parasitemia, gametocyte density, and
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
    **Include_DataByTimeAndPfPRBinsAndAgeBins**, boolean, 0, 1, 1, "When set to true, the 'DataByTimeAndPfPRBinsAndAgeBins' element is included in the report.  Default is true.  You can save disk space by setting this to false."
    **Include_DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins**, boolean, 0, 1, 0, "When set to true, the 'DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins' element is included in the report.  Default is true.  You can save disk space by setting this to false."
    **Add_True_Density_Vs_Threshold**, boolean, 0, 1, 0, "If set to true, four new channels will be added to the report that use true density instead of measured.  These additional channels are: 'PfPR_2to10-True', 'PfPR by Age Bin-True', 'Pf Gametocyte Prevalence by Age Bin-True', and 'Mean Log Parasite Density by Age Bin-True'.  The true densities will be compared to thresholds: Detection_Threshold_True_Parasite_Density and Detection_Threshold_True_Gametocyte_Density."
    **Detection_Threshold_True_Parasite_Density**, 0, 3.40282e+38, 0, "Used when 'Add_True_Density_Vs_Threshold' is true.  The true parasite density is compared against this threshold.  It impacts the 'PfPR_2to10-True', 'PfPR by Age Bin-True', and 'Mean Log Parasite Density by Age Bin-True' channels."
    **Detection_Threshold_True_Gametocyte_Density**,0, 3.40282e+38, 0, "Used when 'Add_True_Density_Vs_Threshold' is true.  The true gametocyte density is compared against this threshold.  It impacts the 'Pf Gametocyte Prevalence by Age Bin-True' channel."
    **Add_Prevalence_By_HRP2**, boolean, 0, 1, 0, "If true, the 'PfPR_2to10-HRP2' and the 'PfPR by Age Bin-HRP2' channels will be added.  These channels will use 'Detection_Threshold_True_HRP2' to determine if person's HRP2 level counts towards prevalence."
    **Detection_Threshold_True_HRP2**, 0, 3.40282e+38, 0, "Used when 'Add_Prevalence_By_HRP2' is true.  If the true HRP2 value is greater than this threshold, the prevalence will be increased in the 'PfPR_2to10-HRP2' and the 'PfPR by Age Bin-HRP2' channels."


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
            },
            "Include_DataByTimeAndPfPRBinsAndAgeBins": 0,
            "Include_DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins": 0,
            "Add_True_Density_Vs_Threshold": 1,
            "Detection_Threshold_True_Parasite_Density": 40.0,
            "Detection_Threshold_True_Gametocyte_Density":, 1.0,
            "Add_Prevalence_By_HRP2": 1,
            "Detection_Threshold_True_HRP2":, 1000000.0
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
    PfPR_2to10, "The fraction of individuals whose age is 2 < age < 10 that would have been detected with the BLOOD_SMEAR_PARASITES diagnostic type of MalariaDiagnostic where the sensitivity is **Report_Parasites_Smear_Sensitivity** and the detection threshold is zero.  Please note that his measurement includes some random noise."
    PfPR_2to10-True, "If **Add_True_Density_Vs_Threshold** is true, this chanel is added.  It will contain the fraction of individuals whose age is 2 < age < 10 and whose true parasite density is greater than **Detection_Threshold_True_Parasite_Density**."
    PfPR_2to10-HRP2, "If **Add_Prevalence_By_HRP2** is true, this chanel is added.  It will contain the fraction of individuals whose age is 2 < age < 10 and whose true HRP2 density is greater than **Detection_Threshold_True_HRP2**."
    No Infection Streak, The maximum number of days without an infection during the interval.
    Fraction Days Under 1pct Infected, The percentage of days during the interval in which the percentage of infected individuals was less than 1%.


DataByTimeAndAgeBins
--------------------

This section contains statistics in two-dimensional arrays by Time (the reporting interval) and
Age Bin.

.. csv-table::
    :header: Parameter, Description
    :widths: 8, 20

    PfPR by Age Bin, "The fraction of individuals in this age bin that would have been detected using the BLOOD_SMEAR_PARASITES diagnostic type of the MalariaDiagnostic intervention where the sensitivity is **Report_Parasites_Smear_Sensitivity** and the detection threshold is zero.  Please note that his measurement includes some random noise."
    PfPR by Age Bin-True, "If **Add_True_Density_Vs_Threshold** is true, this chanel is added.  The fraction of individuals in this age bin whose true parasite density is greater than **Detection_Threshold_True_Parasite_Density**."
    PfPR by Age Bin-HRP2, "If **Add_Prevalence_By_HRP2** is true, this chanel is added.  The fraction of individuals in this age bin whose true HRP2 density is greater than **Detection_Threshold_True_HRP2**."
    Pf Gametocyte Prevalence by Age Bin, "The fraction of individuals in this age bin that would have been detected using the BLOOD_SMEAR_GAMETOCYTES diagnostic type of the MalariaDiagnostic intervention where the sensitivity is **Report_Gametocyte_Smear_Sensitivity** and the detection threshold is 0.02.  Please note that his measurement includes some random noise."
    Pf Gametocyte Prevalence by Age Bin-True, "If **Add_True_Density_Vs_Threshold** is true, this chanel is added.  It will contain the fraction of individuals in this age bin whose true gametocyte density is greater than **Detection_Threshold_True_Gametocyte_Density**."
    Mean Log Parasite Density by Age Bin, "The average Log10 parasite density of the population for that age bin based on the count of parasites using the BLOOD_SMEAR_PARASITES diagnostic type of MalariaDiagnostic where the sensitivity is **Report_Parasites_Smear_Sensitivity**.  Please note that his measurement includes some random noise."
    Mean Log Parasite Density by Age Bin-True, "If **Add_True_Density_Vs_Threshold** is true, this chanel is added.  It will contain the average Log10 parasite density of the population for that age bin based on the count of true parasites."
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

    PfPR by Parasitemia and Age Bin, "The fraction of individuals whose true parasite density and age fall into this bin. The sum of the people whose true parasite density in the PfPRBin and age bin divided by the total number of people in the age bin.  Please note that people who are infected, but have zero parasitemia (i.e. only gametocytes) are counted in the bin that includes zero and is not. This channel is not affected by **Detection_Threshold_True_Parasite_Density** threshold."
    PfPR by Gametocytemia and Age Bin, "The fraction of individuals whose true gametocyte density and age fall into this gametocyte bin. Please note that people who are infected, but have zero gametocytes (i.e. only parasites) are counted in the bin that includes zero. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
    Smeared PfPR by Parasitemia and Age Bin, "The fraction of individuals in this age bin whose true parasite density when smeared by CountPositiveSlideFields falls into this parasitemia bin. This channel is not affected by **Detection_Threshold_True_Parasite_Density** threshold."
    Smeared PfPR by Gametocytemia and Age Bin, "The fraction of individuals in this age bin whose true gametocyte density when smeared by CountPositiveSlideFields falls into this gametocyte bin. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
    Smeared True PfPR by Parasitemia and Age Bin, "The fraction of individuals in this age bin whose true parasite density when smeared by NASBADensityWithUncertainty falls into this parasitemia bin. This channel is not affected by **Detection_Threshold_True_Parasite_Density** threshold."
    Smeared True PfPR by Gametocytemia and Age Bin, "The fraction of individuals in this age bin whose true gametocyte density when smeared by NASBADensityWithUncertainty falls into this parasitemia bin. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."


DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins
----------------------------------------------------

This section contains statistics in four-dimensional arrays: Time (the reporting interval),
Infectiousness, Parasitemia Bins, and Age Bins.


.. csv-table::
    :header: Parameter, Description
    :widths: 8, 20

    Infectiousness by Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness, true gametocyte density, and age fall into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
    Age scaled Infectiousness by Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is scaled by their age-dependent Surface Area Biting, true gametocyte density and age fall into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
    Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age fall into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
    Smeared Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is smeared by BinomialInfectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age falls into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
    Age scaled Smeared Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is first scaled by Surface Area Biting and then smeared by BinomialInfectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age falls into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."



Example
=======


The following is a sample of a MalariaSummaryReport.json file.

.. literalinclude:: ../json/report-malaria-summary.json
   :language: json

