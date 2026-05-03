# MalariaImmunityReport


The malaria immunity report (MalariaImmunityReport.json) is a JSON-formatted file that provides
statistics for several antibody types for specified age bins over a specified reporting duration.
Specifically, the report tracks the average and standard deviation in the fraction of observed
antibodies for *merozoite surface protein (MSP)*, :term:`Plasmodium falciparum erythrocyte
membrane protein 1 (PfEMP1)`, and non-specific (and less immunogenic) minor surface epitopes. The
total amount possible is determined by the parameters **Falciparum_MSP_Variants**,
**Falciparum_PfEMP1_Variants**, and **Falciparum_Nonspecific_Types**. The greater the fraction, the
more antibodies the individual has against possible new infections. The smaller the fraction, the
more naive the individual’s immune system is to malaria.





## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
**Filename_Suffix**, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
**Start_Day**,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
**End_Day**,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
**Node_IDs_Of_Interest**,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list.  Empty list implies all nodes."
**Reporting_Interval**, integer, 1, 1000000, 1000000, "Defines the cadence of the report by specifying how many time steps to collect data before writing to the file. This will limit system memory usage and is advised when large output files are expected."
**Max_Number_Reports**, integer, 0, 1000000, 1, The maximum number of report output files that will be produced for a given campaign.
**Pretty_Format**, boolean, 0, 1, 0, "True (1) sets pretty JSON formatting. The default, false (0), saves space."
**Age_Bins**, array of integers, 0, 125, [ ], "The age bins (in years, in ascending order) to aggregate within and report. An empty array does not stratify by age."
```

```json
{
    "Reports": [
        {
            "class": "MalariaImmunityReport",
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
            "Start_Day": 365,
            "End_Day": 465,
            "Filename_Suffix": "Node1",
            "Node_IDs_Of_Interest": [ 1 ],
            "Reporting_Interval": 10,
            "Max_Number_Reports": 1,
            "Pretty_Format": 1
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data


The report contains the following output data.

```
Age Bins, array of integers, "The array of age bins used in the report (in years)."
MSP Mean by Age Bin, float, "The average fraction of merozoite surface protein (MSP) antibodies over the total possible (**Falciparum_MSP_Variants**) an individual has for each age bin for each reporting interval."
Non-Specific Mean by Age Bin, float, "The average fraction of less-immunogenic minor surface epitopes (non-specific) an individual has developed antibodies for over the total possible (**Falciparum_Nonspecific_Types**) for each age bin for each reporting interval."
PfEMP1 Mean by Age Bin, float, "The average fraction of Plasmodium falciparum erythrocyte membrane protein 1 (PfEMP1) antigens for which an individual has developed antibodies for over the total possible (**Falciparum_PfEMP1_Variants**) for each age bin for each reporting interval."
MSP StdDev by Age Bin, float, "TThe standard deviation for the fraction of merozoite surface protein (MSP) seen by an individual for each age bin for each reporting interval."
Non-Specific StdDev by Age Bin, float, "The standard deviation for the fraction of less-immunogenic minor surface epitopes (non-specific) seen by an individual for each age bin for each reporting interval."
PfEMP1 StdDev by Age Bin, float, "The standard deviation for the fraction of Plasmodium falciparum erythrocyte membrane protein 1 (PfEMP1) seen by the individual for each age bin for each reporting interval."
```

## Example


The following is an example of MalariaImmunityReport.json. Notice there are five age bins and two reporting intervals.

```json
{
    "Age Bins": [
        25,
        50,
        75,
        100,
        125
    ],
    "MSP Mean by Age Bin": [
        [
            0.8632667310552,
            0.8663234088753,
            0.8725000023842,
            0.857499986887,
            0.8826284248331
        ],
        [
            0.8624046362191,
            0.8712405961259,
            0.873493152122,
            0.857499986887,
            0.8831850525747
        ]
    ],
    "Non-Specific Mean by Age Bin": [
        [
            0.7913650278989,
            0.9880864695119,
            0.9972526126973,
            1,
            1
        ],
        [
            0.7751695395588,
            0.9881515987902,
            0.9972555594525,
            1,
            1
        ]
    ],
    "PfEMP1 Mean by Age Bin": [
        [
            0.9790955765201,
            0.979491552852,
            0.9802499935031,
            0.9786335564639,
            0.9819375015795
        ],
        [
            0.9790281954887,
            0.979908272019,
            0.9804023946189,
            0.9790821977674,
            0.9818309637788
        ]
    ],
    "MSP StdDev by Age Bin": [
        [
            0.03146989378593,
            0.03586982024275,
            0.01299036866778,
            0.02046338790071,
            0.02644183223304
        ],
        [
            0.03046207382119,
            0.036680426133,
            0.01342621718435,
            0.02046338790071,
            0.02496969378762
        ]
    ],
    "Non-Specific StdDev by Age Bin": [
        [
            0.2602374122976,
            0.01315735830347,
            0.00446382233485,
            0,
            0
        ],
        [
            0.2789481711119,
            0.01310852104812,
            0.004462334073195,
            0,
            0
        ]
    ],
    "PfEMP1 StdDev by Age Bin": [
        [
            0.005103897532884,
            0.005738237822243,
            0.002277617507036,
            0.002825865931333,
            0.004145300627574
        ],
        [
            0.005032654177563,
            0.005761350326143,
            0.002171759356921,
            0.002869313618544,
            0.004228758281701
        ]
    ]
}
```
