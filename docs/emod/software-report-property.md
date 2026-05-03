# PropertyReport


The property output report  (PropertyReport.json) is a JSON-formatted file with the *channel*
output results of the simulation, defined by the groups set up using **IndividualProperties** in the
demographics file. See [NodeProperties and IndividualProperties](parameter-demographics.md:nodeproperties-and-individualproperties) for more information.   The report contains the count
of individuals with each possible IP key-value combination. The < channel-title > tells you the
statistic and property that are being counted. For example, it allows you to compare disease deaths
for people in the high risk group versus the low risk group.

To generate the property report, set the **Enable_Property_Output** configuration
parameter to 1.

The file contains a header and a channels section.

## Header


The header section contains the following parameters.

```
DateTime, string, The time stamp indicating when the report was generated.
DTK_Version, string, The version of EMOD used.
Report_Type, string, The type of output report.
Report_Version, string, The format version of the report.
Start_Time, integer, The time noted in days when the simulation begins.
Simulation_Timestep, integer, The number of days in each time step.
Timesteps, integer, The number of time steps in this simulation.
Channels, integer, The number of channels in the simulation.
```

## Channels


The channels section contains the following parameters.

```
<Channel_Title>, string, "The title of the particular property channel. The channel titles use the following conventions: for a single property, <channel type>:<property>:<value>, and for multiple properties, <channel type>:<property 1>:<value>,<property 2>:<value>. For example, Infected:Accessibility:Easy or New Infections:Accessibility:Difficult,Risk:High."
Units, string, The units used for this channel.
Data, array, A list of the channel data at each time step.
```

### Channel_Title


The following information is available for the <Channel_Title> parameters. Note that these channels
will have separate sections for each **IndividualProperites** key:value pair.

```
Disease Deaths, The number of people who died from an infection that day.
Infected, "The number of people who have at least one infection on that day. These infections could be so new that they are not detectable via a diagnostic."
New Infections, The number of people with new infections that day.
Statistical Population, The total number of people in the simulation that day.
```

## Example


The following is a sample of a PropertyReport.json file.

```json
{
    "Header": {
        "DateTime": "Mon Feb 15 21:49:24 2016",
        "DTK_Version": "5538 trunk 2015/08/07 14:40:43",
        "Report_Type": "InsetChart",
        "Report_Version": "3.2",
        "Start_Time": 0,
        "Simulation_Timestep": 1,
        "Timesteps": 10,
        "Channels": 8
    },
    "Channels": {
        "Disease Deaths:Accessibility:Easy": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]
        },
        "Disease Deaths:Accessibility:Hard": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]
        },
        "Infected:Accessibility:Easy": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]
        },
        "Infected:Accessibility:Hard": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]
        },
        "New Infections:Accessibility:Easy": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]
        },
        "New Infections:Accessibility:Hard": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]
        },
        "Statistical Population:Accessibility:Easy": {
            "Units": "",
            "Data": [
                6946,
                6946,
                6946,
                6946,
                6946,
                6946,
                6946,
                6946,
                6946,
                6946
            ]
        },
        "Statistical Population:Accessibility:Hard": {
            "Units": "",
            "Data": [
                3054,
                3054,
                3054,
                3054,
                3054,
                3054,
                3054,
                3054,
                3054,
                3054
            ]
        }
    }
}
```
