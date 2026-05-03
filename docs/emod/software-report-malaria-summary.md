# MalariaSummaryReport


The malaria summary report (MalariaSummaryReport.json) is a JSON-formatted report that provides a
population-level summary of malaria data grouped into different bins such as age, parasitemia, gametocyte density, and
infectiousness.



## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
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
```

```json
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
```

## Output file data


These output files may be very large. They contain several sections of data:

* Metadata
* DataByTime
* DataByTimeAndAgeBins
* DataByTimeAndPfPRBinsAndAgeBins
* DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins



### Metadata


This section contains the group of parameters used to configure the report, and includes the following
data channels:

```
**Start_Day**, integer, The first day that the first interval started.
**Reporting_Interval**, integer, The number of days to accumulate data.
**Age Bins**, array of integers, "The max age in years per bin, listed in ascending order.  Note that by using a large value for the last bin, it will  collect all remaining people."
**Parasitemia Bins**, array of integers, "The max parasite density in infected red blood cells per microliter per bin, listed in ascending order."
**Gametocytemia Bins**, array of integers, "The max gametocyte density in infected red blood cells per microliter per bin, listed in ascending order."
**Infectiousness Bins**, array of integers, "The max percent infectiousness of each bin, listed in ascending order."
```

### DataByTime


This section contains a group of statistics where there is just one entry for each reporting interval.
The following statistics are collected:

```
Time Of Report, "Each entry is the final day of the reporting interval, in days."
Annual EIR, "The average Entomological Inoculation Rate (EIR) per year over the reporting interval."
PfPR_2to10, "The fraction of individuals whose age is 2 < age < 10 that would have been detected with the BLOOD_SMEAR_PARASITES diagnostic type of MalariaDiagnostic where the sensitivity is **Report_Parasites_Smear_Sensitivity** and the detection threshold is zero.  Please note that his measurement includes some random noise."
PfPR_2to10-True, "If **Add_True_Density_Vs_Threshold** is true, this chanel is added.  It will contain the fraction of individuals whose age is 2 < age < 10 and whose true parasite density is greater than **Detection_Threshold_True_Parasite_Density**."
PfPR_2to10-HRP2, "If **Add_Prevalence_By_HRP2** is true, this chanel is added.  It will contain the fraction of individuals whose age is 2 < age < 10 and whose true HRP2 density is greater than **Detection_Threshold_True_HRP2**."
No Infection Streak, The maximum number of days without an infection during the interval.
Fraction Days Under 1pct Infected, The percentage of days during the interval in which the percentage of infected individuals was less than 1%.
```

### DataByTimeAndAgeBins


This section contains statistics in two-dimensional arrays by Time (the reporting interval) and
Age Bin.

```
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
```

### DataByTimeAndPfPRBinsAndAgeBins


This section contains statistics in three-dimensional arrays: Time (the reporting interval),
Parasitemia Bins, and Age Bins.

```
PfPR by Parasitemia and Age Bin, "The fraction of individuals whose true parasite density and age fall into this bin. The sum of the people whose true parasite density in the PfPRBin and age bin divided by the total number of people in the age bin.  Please note that people who are infected, but have zero parasitemia (i.e. only gametocytes) are counted in the bin that includes zero. This channel is not affected by **Detection_Threshold_True_Parasite_Density** threshold."
PfPR by Gametocytemia and Age Bin, "The fraction of individuals whose true gametocyte density and age fall into this gametocyte bin. Please note that people who are infected, but have zero gametocytes (i.e. only parasites) are counted in the bin that includes zero. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
Smeared PfPR by Parasitemia and Age Bin, "The fraction of individuals in this age bin whose true parasite density when smeared by CountPositiveSlideFields falls into this parasitemia bin. This channel is not affected by **Detection_Threshold_True_Parasite_Density** threshold."
Smeared PfPR by Gametocytemia and Age Bin, "The fraction of individuals in this age bin whose true gametocyte density when smeared by CountPositiveSlideFields falls into this gametocyte bin. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
Smeared True PfPR by Parasitemia and Age Bin, "The fraction of individuals in this age bin whose true parasite density when smeared by NASBADensityWithUncertainty falls into this parasitemia bin. This channel is not affected by **Detection_Threshold_True_Parasite_Density** threshold."
Smeared True PfPR by Gametocytemia and Age Bin, "The fraction of individuals in this age bin whose true gametocyte density when smeared by NASBADensityWithUncertainty falls into this parasitemia bin. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
```

### DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins


This section contains statistics in four-dimensional arrays: Time (the reporting interval),
Infectiousness, Parasitemia Bins, and Age Bins.


```
Infectiousness by Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness, true gametocyte density, and age fall into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
Age scaled Infectiousness by Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is scaled by their age-dependent Surface Area Biting, true gametocyte density and age fall into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age fall into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
Smeared Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is smeared by BinomialInfectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age falls into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
Age scaled Smeared Infectiousness by smeared Gametocytemia and Age Bin, "The fraction of individuals whose true infectiousness is first scaled by Surface Area Biting and then smeared by BinomialInfectiousness, gametocyte density smeared by NASBADensityWithUncertainty, and age falls into these bins. This channel is not affected by **Detection_Threshold_True_Gametocyte_Density** threshold."
```

## Example



The following is a sample of a MalariaSummaryReport.json file.

```json
{
    "Metadata": {
        "Start_Day": 0,
        "Reporting_Interval": 73,
        "Age Bins": [
            25,
            50,
            75,
            125
        ],
        "Parasitemia Bins": [
            500,
            50000,
            9999999
        ],
        "Gametocytemia Bins": [
            500,
            50000,
            9999999
        ],
        "Infectiousness Bins": [
            50,
            100
        ]
    },
    "DataByTime": {
        "Time Of Report": [
            73,
            146,
            219
        ],
        "Annual EIR": [
            3.162024962367,
            17.51441525354,
            11.87080321251
        ],
        "PfPR_2to10": [
            0.1704726251755,
            0.4665846270352,
            0.7762127578304
        ],
        "No Infection Streak": [
            0,
            0,
            0
        ],
        "Fraction Days Under 1pct Infected": [
            0,
            0,
            0
        ]
    },
    "DataByTimeAndAgeBins": {
        "PfPR by Age Bin": [
            [
                0.1339885339885,
                0.09905544651619,
                0.09631578947368,
                0.05854084753167
            ],
            [
                0.4092613233357,
                0.3057670056635,
                0.301073312716,
                0.3378867014865
            ],
            [
                0.6964023568685,
                0.4945852743663,
                0.5197093551317,
                0.5671100362757
            ]
        ],
        "Pf Gametocyte Prevalence by Age Bin": [
            [
                0.101678951679,
                0.0721908734053,
                0.07070175438596,
                0.0349497597204
            ],
            [
                0.3455263957848,
                0.2407892332988,
                0.2230307440422,
                0.2619525914022
            ],
            [
                0.6942707181209,
                0.4758303587634,
                0.511353315168,
                0.5461507456671
            ]
        ],
        "Mean Log Parasite Density": [
            [
                2.306478442565,
                1.629361294962,
                1.661861693924,
                1.524076431545
            ],
            [
                2.401303822193,
                1.681284855785,
                1.677762827268,
                1.61520629859
            ],
            [
                2.423047828561,
                1.609734215751,
                1.605083507743,
                1.682926607454
            ]
        ],
        "Annual Clinical Incidence by Age Bin": [
            [
                1.741298153531,
                0.2686457410455,
                0.3201754391193,
                0.1594582796097
            ],
            [
                4.401155002415,
                0.9113330598921,
                0.863198146224,
                0.4399356991053
            ],
            [
                6.150984396227,
                0.8612136561424,
                0.7293369323015,
                1.618299007416
            ]
        ],
        "Annual Severe Incidence by Age Bin": [
            [
                1.091113864444,
                0.08954858034849,
                0.1921052634716,
                0
            ],
            [
                3.017934858799,
                0.4445527121425,
                0.3319992870092,
                0.1466452330351
            ],
            [
                3.611317807809,
                0.3312360215932,
                0.4641235023737,
                0.4413542747498
            ]
        ],
        "Average Population by Age Bin": [
            [
                669.0410958904,
                223.3424657534,
                78.08219178082,
                31.35616438356
            ],
            [
                675.9589041096,
                224.9452054795,
                75.30136986301,
                34.09589041096
            ],
            [
                681.1917808219,
                226.4246575342,
                75.41095890411,
                33.98630136986
            ]
        ],
        "Annual Severe Incidence by Anemia by Age Bin": [
            [
                0,
                0,
                0,
                0
            ],
            [
                0,
                0,
                0,
                0
            ],
            [
                0.007340076845139,
                0,
                0,
                0
            ]
        ],
        "Annual Severe Incidence by Parasites by Age Bin": [
            [
                0,
                0,
                0,
                0
            ],
            [
                0,
                0,
                0,
                0
            ],
            [
                0.007340076845139,
                0,
                0,
                0
            ]
        ],
        "Annual Severe Incidence by Fever by Age Bin": [
            [
                1.091113864444,
                0.08954858034849,
                0.1921052634716,
                0
            ],
            [
                3.017934858799,
                0.4445527121425,
                0.3319992870092,
                0.1466452330351
            ],
            [
                3.596637654118,
                0.3312360215932,
                0.4641235023737,
                0.4413542747498
            ]
        ],
        "Annual Severe Anemia": [
            [
                0,
                0,
                0,
                0
            ],
            [
                0,
                0,
                0,
                0
            ],
            [
                0,
                0,
                0,
                0
            ]
        ],
        "Annual Moderate Anemia": [
            [
                0.05978706106544,
                0,
                0,
                0
            ],
            [
                1.33144184947,
                0,
                0,
                0
            ],
            [
                9.461359053385,
                0,
                0,
                0
            ]
        ],
        "Annual Mild Anemia": [
            [
                4.087940300349,
                0,
                0,
                0
            ],
            [
                21.04417812079,
                0,
                0,
                0
            ],
            [
                43.99642060976,
                0,
                0,
                0
            ]
        ]
    },
    "DataByTimeAndPfPRBinsAndAgeBins": {
        "PfPR by Parasitemia and Age Bin": [
            [
                [
                    0.2156224406224,
                    0.2732458292444,
                    0.2470175438596,
                    0.1799912625601
                ],
                [
                    0.04694922194922,
                    0.005642787046124,
                    0.005789473684211,
                    0.001310615989515
                ],
                [
                    0.0009213759213759,
                    0,
                    0,
                    0
                ]
            ],
            [
                [
                    0.512513932516,
                    0.6836368065282,
                    0.6470802255776,
                    0.7127360385697
                ],
                [
                    0.1522342689229,
                    0.02052250167468,
                    0.01691831908314,
                    0.01044596223383
                ],
                [
                    0.004519201540176,
                    0,
                    0,
                    0
                ]
            ],
            [
                [
                    0.6575100046253,
                    0.9105814023837,
                    0.9227974568574,
                    0.9621120515921
                ],
                [
                    0.2662738552497,
                    0.02014640934116,
                    0.02288828337875,
                    0.03385731559855
                ],
                [
                    0.005268767470388,
                    0,
                    0,
                    0
                ]
            ]
        ],
        "PfPR by Gametocytemia and Age Bin": [
            [
                [
                    0.231981981982,
                    0.2774165848871,
                    0.2522807017544,
                    0.1813018785496
                ],
                [
                    0.03151105651106,
                    0.001472031403337,
                    0.0005263157894737,
                    0
                ],
                [
                    0,
                    0,
                    0,
                    0
                ]
            ],
            [
                [
                    0.5678792177526,
                    0.6973996711528,
                    0.6556303438239,
                    0.7219766974689
                ],
                [
                    0.1013881852265,
                    0.006759637050119,
                    0.00836820083682,
                    0.001205303334673
                ],
                [
                    0,
                    0,
                    0,
                    0
                ]
            ],
            [
                [
                    0.6901079896233,
                    0.9226208482062,
                    0.9375113533152,
                    0.9794437726723
                ],
                [
                    0.238944637722,
                    0.008106963518664,
                    0.008174386920981,
                    0.01652559451834
                ],
                [
                    0,
                    0,
                    0,
                    0
                ]
            ]
        ],
        "Smeared PfPR by Parasitemia and Age Bin": [
            [
                [
                    0.2155814905815,
                    0.2731231599607,
                    0.2470175438596,
                    0.1799912625601
                ],
                [
                    0.02661752661753,
                    0.004600098135427,
                    0.005087719298246,
                    0.001310615989515
                ],
                [
                    0.02129402129402,
                    0.001165358194308,
                    0.0007017543859649,
                    0
                ]
            ],
            [
                [
                    0.5121288884385,
                    0.6835150112661,
                    0.6470802255776,
                    0.7127360385697
                ],
                [
                    0.07591447968386,
                    0.01583338408136,
                    0.01273421866473,
                    0.00964242667738
                ],
                [
                    0.08122403485662,
                    0.00481091285549,
                    0.00418410041841,
                    0.0008035355564484
                ]
            ],
            [
                [
                    0.6564844048505,
                    0.9105814023837,
                    0.9235240690282,
                    0.9621120515921
                ],
                [
                    0.1494962495224,
                    0.01675842458709,
                    0.01743869209809,
                    0.02700523982265
                ],
                [
                    0.1230719729724,
                    0.003387984754069,
                    0.0047229791099,
                    0.006852075775897
                ]
            ]
        ],
        "Smeared PfPR by Gametocytemia and Age Bin": [
            [
                [
                    0.2318386568387,
                    0.2772325809617,
                    0.2521052631579,
                    0.1813018785496
                ],
                [
                    0.02223587223587,
                    0.001656035328754,
                    0.0007017543859649,
                    0
                ],
                [
                    0.009418509418509,
                    0,
                    0,
                    0
                ]
            ],
            [
                [
                    0.5678589522748,
                    0.6966688995798,
                    0.6549026741859,
                    0.7219766974689
                ],
                [
                    0.06651129800385,
                    0.007490408623105,
                    0.009095870474804,
                    0.001205303334673
                ],
                [
                    0.03489715270037,
                    0,
                    0,
                    0
                ]
            ],
            [
                [
                    0.6902889778189,
                    0.9221368503842,
                    0.9378746594005,
                    0.9774284562676
                ],
                [
                    0.1544834797997,
                    0.008590961340674,
                    0.007811080835604,
                    0.01854091092301
                ],
                [
                    0.08428016972671,
                    0,
                    0,
                    0
                ]
            ]
        ],
        "Smeared True PfPR by Parasitemia and Age Bin": [
            [
                [
                    0.2124488124488,
                    0.2658856722277,
                    0.2410526315789,
                    0.176496286588
                ],
                [
                    0.04928337428337,
                    0.012941609421,
                    0.01175438596491,
                    0.004805591961555
                ],
                [
                    0.001760851760852,
                    6.133464180569e-05,
                    0,
                    0
                ]
            ],
            [
                [
                    0.5028675651028,
                    0.6659155958833,
                    0.6308895761324,
                    0.6958617918843
                ],
                [
                    0.1583341777282,
                    0.03781742890202,
                    0.03310896852829,
                    0.02732020891924
                ],
                [
                    0.008065660147938,
                    0.0004262834175751,
                    0,
                    0
                ]
            ],
            [
                [
                    0.6451022583305,
                    0.8832960251679,
                    0.8986376021798,
                    0.9338976219266
                ],
                [
                    0.273412834074,
                    0.0470082884627,
                    0.04668483197094,
                    0.06207174526401
                ],
                [
                    0.01053753494078,
                    0.0004234980942586,
                    0.0003633060853769,
                    0
                ]
            ]
        ],
        "Smeared True PfPR by Gametocytemia and Age Bin": [
            [
                [
                    0.2295864045864,
                    0.2739205103042,
                    0.249298245614,
                    0.1804281345566
                ],
                [
                    0.03355855855856,
                    0.004968105986261,
                    0.003508771929825,
                    0.00087374399301
                ],
                [
                    0.0003480753480753,
                    0,
                    0,
                    0
                ]
            ],
            [
                [
                    0.55768568244,
                    0.6868643809756,
                    0.6450791340731,
                    0.711530735235
                ],
                [
                    0.110163137096,
                    0.01692954144084,
                    0.0187374931781,
                    0.0116512655685
                ],
                [
                    0.001418583443105,
                    0.0003653857864929,
                    0.0001819174094961,
                    0
                ]
            ],
            [
                [
                    0.6753272869869,
                    0.9037449331478,
                    0.9171662125341,
                    0.9532446594115
                ],
                [
                    0.2512920546182,
                    0.0269223788493,
                    0.0283378746594,
                    0.04272470777912
                ],
                [
                    0.002433285740141,
                    6.049972775123e-05,
                    0.0001816530426885,
                    0
                ]
            ]
        ]
    },
    "DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins": {
        "Infectiousness by Gametocytemia and Age Bin": [
            [
                [
                    [
                        0.1968468468468,
                        0.2587708537782,
                        0.2326315789474,
                        0.176496286588
                    ],
                    [
                        0.0001228501228501,
                        0,
                        0,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.03513513513514,
                        0.01864573110893,
                        0.01964912280702,
                        0.004805591961555
                    ],
                    [
                        0.03138820638821,
                        0.001472031403337,
                        0.0005263157894737,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.4628635120073,
                        0.6436270629073,
                        0.5995997816991,
                        0.6777822418642
                    ],
                    [
                        0.001013273887932,
                        0,
                        0,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.1050157057453,
                        0.05377260824554,
                        0.0560305621248,
                        0.04419445560466
                    ],
                    [
                        0.1003749113385,
                        0.006759637050119,
                        0.00836820083682,
                        0.001205303334673
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.4698855752408,
                        0.8167463246415,
                        0.8207084468665,
                        0.8363563079403
                    ],
                    [
                        0.00166911335894,
                        0,
                        0,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.2202224143825,
                        0.1058745235646,
                        0.1168029064487,
                        0.143087464732
                    ],
                    [
                        0.237275524363,
                        0.008106963518664,
                        0.008174386920981,
                        0.01652559451834
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ]
        ],
        "Age scaled Infectiousness by Gametocytemia and Age Bin": [
            [
                [
                    [
                        0.2228705978706,
                        0.2587708537782,
                        0.2326315789474,
                        0.176496286588
                    ],
                    [
                        0.02727272727273,
                        0,
                        0,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.009111384111384,
                        0.01864573110893,
                        0.01964912280702,
                        0.004805591961555
                    ],
                    [
                        0.004238329238329,
                        0.001472031403337,
                        0.0005263157894737,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.538453744047,
                        0.6436270629073,
                        0.5995997816991,
                        0.6777822418642
                    ],
                    [
                        0.0857432363968,
                        0,
                        0,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.02942547370554,
                        0.05377260824554,
                        0.0560305621248,
                        0.04419445560466
                    ],
                    [
                        0.01564494882967,
                        0.006759637050119,
                        0.00836820083682,
                        0.001205303334673
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.6135700927062,
                        0.8167463246415,
                        0.8207084468665,
                        0.8363563079403
                    ],
                    [
                        0.2018822772337,
                        0,
                        0,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.07653789691717,
                        0.1058745235646,
                        0.1168029064487,
                        0.143087464732
                    ],
                    [
                        0.03706236048827,
                        0.008106963518664,
                        0.008174386920981,
                        0.01652559451834
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ]
        ],
        "Infectiousness by smeared Gametocytemia and Age Bin": [
            [
                [
                    [
                        0.195515970516,
                        0.2569921491658,
                        0.2308771929825,
                        0.175622542595
                    ],
                    [
                        0.001433251433251,
                        0.001778704612365,
                        0.001754385964912,
                        0.00087374399301
                    ],
                    [
                        2.047502047502e-05,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.03407043407043,
                        0.01692836113837,
                        0.01842105263158,
                        0.004805591961555
                    ],
                    [
                        0.03212530712531,
                        0.003189401373896,
                        0.001754385964912,
                        0
                    ],
                    [
                        0.0003276003276003,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.4565001519911,
                        0.637476402168,
                        0.5950518464617,
                        0.6729610285255
                    ],
                    [
                        0.007234775559834,
                        0.005785274952804,
                        0.004366017827906,
                        0.00482121333869
                    ],
                    [
                        0.0001418583443105,
                        0.0003653857864929,
                        0.0001819174094961,
                        0
                    ]
                ],
                [
                    [
                        0.1011855304489,
                        0.04938797880762,
                        0.05002728761142,
                        0.03856970670952
                    ],
                    [
                        0.1029283615361,
                        0.01114426648803,
                        0.01437147535019,
                        0.006830052229811
                    ],
                    [
                        0.001276725098794,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.4602730910773,
                        0.8069453687458,
                        0.8108991825613,
                        0.826279725917
                    ],
                    [
                        0.01120115832445,
                        0.009740456167947,
                        0.009627611262489,
                        0.01007658202338
                    ],
                    [
                        8.04391980212e-05,
                        6.049972775123e-05,
                        0.0001816530426885,
                        0
                    ]
                ],
                [
                    [
                        0.2150541959097,
                        0.09679956440196,
                        0.1062670299728,
                        0.1269649334946
                    ],
                    [
                        0.2400908962938,
                        0.01718192268135,
                        0.01871026339691,
                        0.03264812575574
                    ],
                    [
                        0.00235284654212,
                        0,
                        0,
                        0
                    ]
                ]
            ]
        ],
        "Smeared Infectiousness by smeared Gametocytemia and Age Bin": [
            [
                [
                    [
                        0.1963963963964,
                        0.2576054955839,
                        0.2315789473684,
                        0.176496286588
                    ],
                    [
                        0.001699426699427,
                        0.001717369970559,
                        0.001929824561404,
                        0.00087374399301
                    ],
                    [
                        2.047502047502e-05,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.03319000819001,
                        0.01631501472031,
                        0.01771929824561,
                        0.003931847968545
                    ],
                    [
                        0.03185913185913,
                        0.003250736015702,
                        0.001578947368421,
                        0
                    ],
                    [
                        0.0003276003276003,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.4584051069004,
                        0.6386334571585,
                        0.5975986901947,
                        0.6765769385295
                    ],
                    [
                        0.007640085115007,
                        0.00566347969064,
                        0.004366017827906,
                        0.003615910004018
                    ],
                    [
                        0.0001418583443105,
                        0.0003653857864929,
                        0.0001819174094961,
                        0
                    ]
                ],
                [
                    [
                        0.09928057553957,
                        0.04823092381706,
                        0.04748044387848,
                        0.0349537967055
                    ],
                    [
                        0.102523051981,
                        0.0112660617502,
                        0.01437147535019,
                        0.008035355564484
                    ],
                    [
                        0.001276725098794,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.4642146117803,
                        0.8050093774578,
                        0.8114441416894,
                        0.8202337767029
                    ],
                    [
                        0.01224686789873,
                        0.009679956440196,
                        0.01017257039055,
                        0.01047964530431
                    ],
                    [
                        8.04391980212e-05,
                        6.049972775123e-05,
                        0.0001816530426885,
                        0
                    ]
                ],
                [
                    [
                        0.2111126752066,
                        0.09873555569,
                        0.1057220708447,
                        0.1330108827086
                    ],
                    [
                        0.2390451867195,
                        0.0172424224091,
                        0.01816530426885,
                        0.03224506247481
                    ],
                    [
                        0.00235284654212,
                        0,
                        0,
                        0
                    ]
                ]
            ]
        ],
        "Age scaled Smeared Infectiousness by smeared Gametocytemia and Age Bin": [
            [
                [
                    [
                        0.2209868959869,
                        0.2587708537782,
                        0.2322807017544,
                        0.1760594145915
                    ],
                    [
                        0.02870597870598,
                        0.001656035328754,
                        0.001754385964912,
                        0.00087374399301
                    ],
                    [
                        0.0003480753480753,
                        0,
                        0,
                        0
                    ]
                ],
                [
                    [
                        0.008599508599509,
                        0.01514965652601,
                        0.01701754385965,
                        0.00436871996505
                    ],
                    [
                        0.00485257985258,
                        0.003312070657507,
                        0.001754385964912,
                        0
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.5295977302665,
                        0.6375981974301,
                        0.5946880116427,
                        0.6753716351949
                    ],
                    [
                        0.09198500354646,
                        0.005785274952804,
                        0.004547935237402,
                        0.00482121333869
                    ],
                    [
                        0.001418583443105,
                        0.0003653857864929,
                        0.0001819174094961,
                        0
                    ]
                ],
                [
                    [
                        0.02808795217347,
                        0.04926618354546,
                        0.05039112243042,
                        0.03615910004018
                    ],
                    [
                        0.0181781335495,
                        0.01114426648803,
                        0.01418955794069,
                        0.006830052229811
                    ],
                    [
                        0,
                        0,
                        0,
                        0
                    ]
                ]
            ],
            [
                [
                    [
                        0.603293985159,
                        0.8082763627564,
                        0.8108991825613,
                        0.825876662636
                    ],
                    [
                        0.2073722524986,
                        0.009740456167947,
                        0.009264305177112,
                        0.01128577186618
                    ],
                    [
                        0.002413175940636,
                        6.049972775123e-05,
                        0.0001816530426885,
                        0
                    ]
                ],
                [
                    [
                        0.07203330182798,
                        0.09546857039143,
                        0.1062670299728,
                        0.1273679967755
                    ],
                    [
                        0.04391980211957,
                        0.01718192268135,
                        0.01907356948229,
                        0.03143893591294
                    ],
                    [
                        2.01097995053e-05,
                        0,
                        0,
                        0
                    ]
                ]
            ]
        ]
    }
}
```
