# BinnedReport


The binned output report  (BinnedReport.json) is a JSON-formatted file where the channel data has
been sorted into age bins. It is very similar to an inset chart, however, with the binned report all
channels are broken down into sub-channels (bins) based on age. For example, instead of
having a single prevalence channel, you might have prevalence in the "0-3 years old bin" and the
"4-6 years old bin, and so forth.

To generate the binned report, set the **Enable_Demographics_Reporting** configuration parameter
to 1. The demographics summary output report will also be generated.

The file contains a header and a channels section.

## Header


The header section contains the following parameters.

```
DateTime, string, The time stamp indicating when the report was generated.
DTK_Version, string, The version of EMOD used.
Report_Type, string, The type of output report.
Report_Version, string, The format version of the report.
Timesteps, integer, The number of time steps in this simulation.
Channels, integer, The number of channels in the simulation.
Subchannel_Metadata, nested JSON object, "Metadata that describes the bins and axis information. The metadata includes the following parameters:
```

| Parameter | Data type | Description |
| --- | --- | --- |
| AxisLabels | array of strings | The name of each axis. |
| NumBinsPerAxis | array of integers | The number of bins per axis. |
| ValuesPerAxis | array of integers | The maximum age in days for each bin in the axis. |
| MeaningPerAxis | array of strings | Shows the ValuesPerAxis values binned by age range, such as younger than 5 years (<5), 5 to 9 (5-9), and so on.  |


## Channels


Malaria binned reports have the following channel data:

```
Blood Smear Gametocyte Positive,"The number of individuals who are detectable with the BLOOD_SMEAR_GAMETOCYTES version of **MalariaDiagnostic** intervention. The detectability of the diagnostic is controlled by parameters **Report_Gametocyte_Smear_Sensitivity** and **Report_Detection_Threshold_Blood_Smear_Gametocytes**."
Blood Smear Parasite Positive,"The number of individuals who are detectable with the BLOOD_SMEAR_PARASITES version of MalariaDiagnostic intervention. The detectability of the diagnostic is controlled by parameters **Report_Parasites_Smear_Sensitivity** and **Report_Detection_Threshold_Blood_Smear_Parasites**."
Fever Positive,"The number of individuals currently with a fever. Detectable fever is determined by the parameter **Report_Detection_Threshold_Fever**. which is the level of temperature above normal (Celsius) for an individual to be considered to have a fever."
Infected,The number of individuals who are infected on that day in that age bin. 
Mean Parasitemia,"The geometric mean number of parasites per microliter of blood. [Exponential of (Sum of log(BLOOD_SMEAR_PARASITES diagnostic ) for all individuals divided by the number of individuals detected using BLOOD_SMEAR_PARASITES) diagnostic - geometric mean]."
New Clinical Cases,"The number of new clinical cases on that day. This channel is controlled by the **Clinical_Fever_Threshold_Low** and **Clinical_Fever_Threshold_High**  parameters. The amount that an individual’s fever is above normal must be greater than both of these values to be considered clinical."
New Infections,"The number of individuals who got infected on that day. This is not the number of new infections on that day. An individual could receive multiple infections in a single day depending on the value of the **Malaria_Model** parameter in your configuration setup."
New Severe Cases,"The number of new severe cases of malaria on that day. An individual is considered to be a severe case if the combined probability of anemia, parasite density, and fever is greater than a uniform random number. This combined probability is the combination of sigmoid using the following parameters: **Anemia_Severe_Threshold** and **Anemia_Severe_Inverse_Width**, **Parasite_Severe_Threshold** and **Parasite_Severe_Inverse_Width** , and **Fever_Severe_Threshold** and **Fever_Severe_Inverse_Width**."
PCR Gametocytes Positive,"The number of individuals who are detectable with the PCR_GAMETOCYTES version of **MalariaDiagnostic**. The detectability of the diagnostic is controlled by parameter **Report_Detection_Threshold_PCR_Gametocytes**."
PCR Parasites Positive,"The number of individuals who are detectable with the PCR_PARASITES version of **MalariaDiagnostic**. The detectability of the diagnostic is controlled by parameter **Report_Detection_Threshold_PCR_Parasites**."
PfHRP2 Positive,"The number of individuals who are detectable with the PF_HRP2 version of **MalariaDiagnostic**. The detectability of the diagnostic is controlled by parameter **Report_Detection_Threshold_PCR_PfHRP2**."
Population,The total number of individuals in this age range on this day. 
Sum MSP Variant Fractions,"This the sum of each individual’s fraction of MSP variants that an individual has had. The parameter **Falciparum_MSP_Variants** defines the total number of possible variants. This channel indicates the average fraction that an individual has seen of this total number. The greater the fraction the more that the population has developed antibodies to the parasite."
Sum Non-Specific Variant Fractions,"This the sum of each individual’s fraction of Non-Specific variants that an individual has had. The parameter **Falciparum_Nonspecific_Types** defines the total number of possible variants. This channel indicates the average fraction that an individual has seen of this total number. The greater the fraction the more that the population has developed antibodies to the parasite."
Sum of Squared MSP Variant Fractions,This is the sum of the squares of the values used in calculating Sum MSP Variant Fractions. 
Sum of Squared Non-Specific Variant Fractions,This is the sum of the squares of the values used in calculating Sum Non-Specific Variant Fractions. 
Sum of Squared PfEMP1 Variant Fractions,This is the sum of the squares of the values used in calculating Sum PfEMP1 Variant Fractions. 
Sum PfEMP1 Variant Fractions,"This the sum of each individual’s fraction of variants of the PfEMP1 var genes that an individual has had. The parameter **Falciparum_PfEMP1_Variants** defines the total number of possible variants. This channel indicates the average fraction that an individual has seen of this total number. The greater the fraction the more that the population has developed antibodies to the parasite."
True Positive,"The number of individuals who are detectable with the TRUE_PARASITE_DENSITY version of **MalariaDiagnostic**. The detectability of the diagnostic is controlled by parameter **Report_Detection_Threshold_True_Parasite_Density**."
```

## Example


The following is a sample of a BinnedReport.json file for malaria.

```json
{
    "Header": {
        "DateTime": "Mon Dec 21 11:33:27 2020",
        "DTK_Version": " Malaria-Ongoing (bb265ad) Dec 21 2020 11:15:31",
        "Report_Version": "2.1",
        "Timesteps": 730,
        "Subchannel_Metadata": {
            "AxisLabels": [
                [
                    "Age"
                ]
            ],
            "NumBinsPerAxis": [
                [
                    21
                ]
            ],
            "ValuesPerAxis": [
                [
                    [
                        1825,
                        3650,
                        5475
                    ]
                ]
            ],
            "MeaningPerAxis": [
                [
                    [
                        "<5",
                        "55-59",
                        "95-99"
                    ]
                ]
            ]
        },
        "Channels": 19
    },
    "Channels": {
        "Blood Smear Gametocyte Positive": {
            "Units": "",
            "Data": [
                [
                    380,
                    300,
                    1670
                ]
            ]
        },
        "Blood Smear Parasite Positive": {
            "Units": "",
            "Data": [
                [
                    90,
                    80,
                    90
                ]
            ]
        },
        "Fever Positive": {
            "Units": "",
            "Data": [
                [
                    1700,
                    1760,
                    1660
                ]
            ]
        },
        "Infected": {
            "Units": "",
            "Data": [
                [
                    1790,
                    1090,
                    1723
                ]
            ]
        }
    }
}
```
