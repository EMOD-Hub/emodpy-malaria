# VectorSpeciesReport


The vector species output report (VectorSpeciesReport.json) is a JSON-formatted file where the
channel data has been sorted into bins. It is identical to the [BinnedReport](software-report-binned.md), with
the exception that the bins are based on vector species, and provides the average number of adult
vectors per node for each species. The vector species report is generated for all malaria or vector
contain values in the **Vector_Species_Params** configuration parameter. For example, if
**Vector_Species_Params** contained "funestus" and "gambiae", you could be able to see the average
number of female vectors per node for both *A. funestus* and *A. gambiae*.

## Configuration

To generate the report, set the **Enable_Vector_Species_Report** configuration parameter to 1.

## Header


The header section contains the following parameters.

| Parameter | Data type | Description |
| --- | --- | --- |
| `DateTime` | string | The time stamp indicating when the report was generated. |
| `DTK_Version` | string | The version of EMOD used. |
| `Report_Type` | string | The type of output report. |
| `Report_Version` | string | The format version of the report. |
| `Timesteps` | integer | The number of timesteps in this simulation. |
| `Channels` | integer | The number of channels in the simulation. |
| `Subchannel_Metadata` | nested JSON object | Metadata that describes the bins and axis information. See the table below for its sub-parameters. |

The `Subchannel_Metadata` object contains the following parameters:

| Parameter | Data type | Description |
| --- | --- | --- |
| `AxisLabels` | array of strings | The name of the axis, Vector Species. |
| `NumBinsPerAxis` | array of integers | The number of bins per axis, one for each species. |
| `ValuesPerAxis` | array of integers | Not applicable for this report, always 0. |
| `MeaningPerAxis` | array of strings | The name of each species as defined in **Vector_Species_Params**. |


## Channels


The channels section contains the following parameters.

| Parameter | Data type | Description |
| --- | --- | --- |
| `<Channel_Title>` | string | The title of the particular channel. |
| `Units` | string | The units used for this channel. |
| `Data` | array | A list of the channel data at each timestep. |

The data channels included are:

| Parameter | Description |
| --- | --- |
| `Adult Vectors Per Node` | The average number of adult female vectors in each node on each day for each species. |
| `Fraction Infectious Vectors` | The fraction of adult female vectors that are infected and infectious. |
| `Daily EIR` | The entomological inoculation rate (EIR), or the number of infected mosquito bites each individual receives each day, on average. |
| `Daily HBR` | The average number of mosquito bites received per individual per day. |
| `Fraction Vectors Died Before Feeding` | The fraction of adult female vectors that die while attempting to feed indoors. This includes death before feeding (e.g. killed by a bednet), during feeding (e.g. squished = **Human_Feeding_Mortality**), and after feeding (e.g. landing on an IRS wall). |
| `Fraction Vectors Died During Outdoor Feeding` | The fraction of vectors that die while attempting to feed outdoors. The causes are typically due to individual-level outdoor interventions. |

## Example


The following is a sample of an VectorSpeciesReport.json file.

```json
{
    "Header": {
        "DateTime": "Mon Dec 21 11:20:38 2020",
        "DTK_Version": "Malaria-Ongoing (bb265ad) Dec 21 2020 11:15:31",
        "Report_Version": "2.1",
        "Timesteps": 180,
        "Subchannel_Metadata": {
            "AxisLabels": [["Vector Species"]],
            "NumBinsPerAxis": [[3]],
            "ValuesPerAxis": [[[0, 0, 0]]],
            "MeaningPerAxis": [[["arabiensis", "funestus", "gambiae"]]]
        },
        "Channels": 7
    },
    "Channels": {
        "Adult Vectors Per Node": {
            "Units": "",
            "Data": [[8795, 7720, 6735]]
        },
        "Daily EIR": {
            "Units": "",
            "Data": [[0.00400000018999, 0.02800000086427, 0.835000038147]]
        },
        "Daily HBR": {
            "Units": "",
            "Data": [[2.785000085831, 8.515999794006, 3.394000053406]]
        },
        "Percent Infectious Vectors": {
            "Units": "",
            "Data": [[0.04697532951832, 0.18621134758, 0.2092223018408]]
        },
        "Percent Vectors Died Before Feeding": {
            "Units": "",
            "Data": [[0.09339272230864, 0.1022477596998, 0.09913764148951]]
        },
        "Percent Vectors Died During Indoor Feeding": {
            "Units": "",
            "Data": [[0.03303108736873, 0.0264107119292, 0.01262986380607]]
        },
        "Percent Vectors Died During Outdoor Feeding": {
            "Units": "",
            "Data": [[0.01304347813129, 0.01427712664008, 0.03279281407595]]
        }
    }
}
```
