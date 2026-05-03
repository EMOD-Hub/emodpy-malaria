# VectorHabitatReport


The vector habitat report is a JSON-formatted file containing the habitat data for each vector
species included in the simulation. It focuses on statistics relevant to mosquito developmental
stages (e.g. eggs and larvae), such as egg capacity and larval crowding.

The output file is a binned JSON report named VectorHabitatReport.json.



## Configuration


You do not need to configure any parameters to generate this report.


## Output file data


### Header


The header section contains the following parameters:

```
Channels, integer, "The number of statistics in the report; this should always be equal to 7."
DateTime, string, The date and time the report was created.
DTK_Version, string, "The version of EMOD that was used."
Report_Version, string, The format version of the report.
Timesteps, integer, "The number of time steps in the simulation (which should be the number of entries in the inner dimension of the data)."
Subchannel_Metadata, nested JSON object, "A collection of parameters defining the contents of the channel data. It includes the following parameters:
```

| Parameter | Data type | Description |
| --- | --- | --- |
| AxisLabels | array of strings | A description about the dimensions of the data which should always be Species:Habitat |
| NumBinsPerAxis | array of integers | The channel arrays are two dimensional and this indicates the size of the outer dimension.  This is the number of habitats for each species. For example, if species 1 has 1 habitat, species 2 has 2 habitats, and species 3 has 3 habitats, this number should be 6. |
| ValuesPerAxis | array of integers | Not applicable for this report. |
| MeaningPerAxis | array of strings | The description of the entries of the outer dimension.  The number of entries in this array should be the value NumBinsPerAxis.  There should be one entry for each habitat of each species. |


### Channels


The channels section contains the following parameters:

```
<Channel_Title>, string, "The title of the particular channel. Possible channels are:
```

| Parameter | Data type | Description |
| --- | --- | --- |
| Artificial Larval Mortality | float | The probability of the larva in the habitat being killed due to interventions (i.e. Larvicides). |
| Current Habitat Capacity | integer | the number of larva that the habitat can currently hold. |
| Egg Crowding Factor | float | The probability that eggs die due to overcrowding. |
| Local Larval Growth Modifier | float | The local density-dependent hatching modifier which depends on larval crowding |
| Local Larval Mortality | float | The local larval mortality rate due to larval competition in the habitat. Note that mortality is relative to a species baseline (1.0) and intermediate larval age (0.5). |
| Rainfall Larval Mortality | float | The rate at which larvae are dying due to rainfall. |
| Total Larva | integer | The total number of larvae of that species in that habitat during that time step. |

```
Units, string, The units used for this channel.
Data, array, "A two-dimensional array of the channel data at each time step where the outer dimension is for each species:habitat and the inner dimension is for each time step."
```

## Example


```json
{
    "Header": {
        "DateTime": "Fri May 17 15:33:03 2019",
        "DTK_Version": "4148 Malaria-Ongoing (bb265ad) May 16 2019 09:39:35",
        "Report_Version": "2.1",
        "Timesteps": 5,
        "Subchannel_Metadata": {
            "AxisLabels": [
                [
                    "Species:Habitat"
                ]
            ],
            "NumBinsPerAxis": [
                [
                    3
                ]
            ],
            "ValuesPerAxis": [
                [
                    [
                        0,
                        0,
                        0
                    ]
                ]
            ],
            "MeaningPerAxis": [
                [
                    [
                        "gambiae:TEMPORARY_RAINFALL",
                        "funestus:WATER_VEGETATION",
                        "arabiensis:TEMPORARY_RAINFALL"
                    ]
                ]
            ]
        },
        "Channels": 7
    },
    "Channels": {
        "Artificial Larval Mortality": {
            "Units": "",
            "Data": [
                [
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0,
                    0,
                    0
                ]
            ]
        },
        "Current Habitat Capacity": {
            "Units": "",
            "Data": [
                [
                    402.5242614746,
                    469.3384094238,
                    482.3938293457,
                    730.068359375,
                    718.5045776367
                ],
                [
                    195.2786865234,
                    230.9520568848,
                    242.8811035156,
                    376.0362548828,
                    384.9170837402
                ],
                [
                    3622.71875,
                    4224.045898438,
                    4341.544433594,
                    6570.615234375,
                    6466.541503906
                ]
            ]
        },
        "Egg Crowding Factor": {
            "Units": "",
            "Data": [
                [
                    1,
                    0.1548170298338,
                    0.01222433708608,
                    0.03274614363909,
                    0.212905973196
                ],
                [
                    1,
                    0.1394847780466,
                    0.03747003525496,
                    0.0134865026921,
                    0.1550362557173
                ],
                [
                    1,
                    1,
                    1,
                    1,
                    1
                ]
            ]
        },
        "Local Larval Growth Modifier": {
            "Units": "",
            "Data": [
                [
                    1,
                    1,
                    1,
                    1,
                    1
                ],
                [
                    1,
                    1,
                    1,
                    1,
                    1
                ],
                [
                    1,
                    1,
                    1,
                    1,
                    1
                ]
            ]
        },
        "Local Larval Mortality": {
            "Units": "",
            "Data": [
                [
                    1,
                    1,
                    1,
                    1,
                    1
                ],
                [
                    1,
                    1,
                    1,
                    1,
                    1
                ],
                [
                    1,
                    1,
                    1,
                    1,
                    1
                ]
            ]
        },
        "Rainfall Larval Mortality": {
            "Units": "",
            "Data": [
                [
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    0,
                    0,
                    0
                ]
            ]
        },
        "Total Larva": {
            "Units": "",
            "Data": [
                [
                    0,
                    440,
                    430,
                    432,
                    721
                ],
                [
                    0,
                    171,
                    224,
                    221,
                    334
                ],
                [
                    0,
                    1600,
                    2840,
                    3978,
                    3987
                ]
            ]
        }
    }
}
```
