# DemographicsSummary


The demographic summary output report (DemographicsSummary.json) is a JSON-formatted file with the
demographic *channel* output results of the simulation, consisting of simulation-wide averages
by time step. The format is identical to the inset chart output report, except the channels reflect
demographic categories, such as gender ratio.

To generate the demographics summary report, set the **Enable_Demographics_Reporting** configuration
parameter to 1. The [software-report-binned](software-report-binned.md) will also be generated.

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
Average Age, integer, "The average age of the Statistical Population at each time step. This takes the age of each agent and multiplies it by the agent's Monte Carlo Weight, adds them together, then divides that sum by the Statistical Population."
"Gender Ratio (fraction male)", integer, "The fraction of the statistical population that is male at each time step.  This takes the Monte Carlo weight of each male, adds them together, then divides by the statistical population."
New Births, integer, "The statistical number of children born during each time step.  This is the sum of the Monte Carlo weight of each newborn."
New Natural Deaths, integer, "The statistical number of people that died from natural causes (i.e. not disease) during each time step.  This is the sum of the Monte Carlo weights of each person that died."
"Population Age X-Y", integer, "The statistical population of the people whose age is greater than or equal to X and strictly less than Y+1.  For example, if X=10 and Y=14, then if 10 <= age < 15, the person will be counted in that channel.  This channel is the sum of the Monte Carlo weight of each person that qualifies for that channel.  The set of channels is starts at 0-5 (i.e.<5) and increases every 5 years until the last bin is those people over 100."
Possible Mothers, integer, The total number of females in the population whose age is greater than 14 years and less than 45 years.
Pseudo-Population, integer, "The number of actual human agents in the simulation on that day. This number times the Monte Carlo Weight (which is controlled by the configuration parameter **Individual_Sampling_Type**) should be the same value as in the Statistical Population channel."
Statistical Population, integer, "The total number of individuals in the simulation on that day. The sum of the Population Age X-Y channels at each time step should sum to this channel at the corresponding time step."
```

## Example


The following is a sample of a DemographicsSummary.json file.

```json
{
    "Header": {
        "DateTime": "Mon Mar 16 07:45:10 2015",
        "DTK_Version": "4777 v2.0-HIV 2015/02/26 10:51:25",
        "Report_Type": "InsetChart",
        "Report_Version": "3.2",
        "Start_Time": 0,
        "Simulation_Timestep": 1,
        "Timesteps": 5,
        "Channels": 28
    },
    "Channels": {
        "Average Age": {
            "Units": "",
            "Data": [
                8592.415039063,
                8593.427734375,
                8594.439453125,
                8595.41796875,
                8596.412109375
            ]
        },
        "Gender Ratio (fraction male)": {
            "Units": "",
            "Data": [
                0.5350999832153,
                0.5350999832153,
                0.5350999832153,
                0.5350999832153,
                0.5350999832153
            ]
        },
        "New Births": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0
            ]
        },
        "New Natural Deaths": {
            "Units": "",
            "Data": [
                0,
                0,
                0,
                0,
                0
            ]
        },
        "Population Age 10-14": {
            "Units": "",
            "Data": [
                1203,
                1204,
                1202,
                1203,
                1203
            ]
        },
        "Population Age 15-19": {
            "Units": "",
            "Data": [
                1056,
                1057,
                1059,
                1059,
                1059
            ]
        },
        "Population Age 20-24": {
            "Units": "",
            "Data": [
                810,
                810,
                810,
                809,
                809
            ]
        },
        "Population Age 25-29": {
            "Units": "",
            "Data": [
                732,
                732,
                732,
                732,
                732
            ]
        },
        "Population Age 30-34": {
            "Units": "",
            "Data": [
                540,
                539,
                539,
                539,
                539
            ]
        },
        "Population Age 35-39": {
            "Units": "",
            "Data": [
                410,
                411,
                411,
                411,
                411
            ]
        },
        "Population Age 40-44": {
            "Units": "",
            "Data": [
                351,
                351,
                351,
                352,
                352
            ]
        },
        "Population Age 45-49": {
            "Units": "",
            "Data": [
                294,
                294,
                294,
                294,
                294
            ]
        },
        "Population Age 5-9": {
            "Units": "",
            "Data": [
                1599,
                1597,
                1598,
                1597,
                1599
            ]
        },
        "Population Age 50-54": {
            "Units": "",
            "Data": [
                201,
                201,
                201,
                201,
                201
            ]
        },
        "Population Age 55-59": {
            "Units": "",
            "Data": [
                194,
                194,
                194,
                193,
                193
            ]
        },
        "Population Age 60-64": {
            "Units": "",
            "Data": [
                163,
                163,
                163,
                164,
                164
            ]
        },
        "Population Age 65-69": {
            "Units": "",
            "Data": [
                111,
                111,
                111,
                111,
                111
            ]
        },
        "Population Age 70-74": {
            "Units": "",
            "Data": [
                104,
                104,
                104,
                103,
                103
            ]
        },
        "Population Age 75-79": {
            "Units": "",
            "Data": [
                86,
                86,
                86,
                87,
                87
            ]
        },
        "Population Age 80-84": {
            "Units": "",
            "Data": [
                55,
                55,
                55,
                55,
                55
            ]
        },
        "Population Age 85-89": {
            "Units": "",
            "Data": [
                61,
                61,
                61,
                61,
                61
            ]
        },
        "Population Age 90-94": {
            "Units": "",
            "Data": [
                49,
                49,
                49,
                49,
                49
            ]
        },
        "Population Age 95-99": {
            "Units": "",
            "Data": [
                30,
                30,
                30,
                30,
                30
            ]
        },
        "Population Age <5": {
            "Units": "",
            "Data": [
                1829,
                1829,
                1828,
                1828,
                1826
            ]
        },
        "Population Age >100": {
            "Units": "",
            "Data": [
                122,
                122,
                122,
                122,
                122
            ]
        },
        "Possible Mothers": {
            "Units": "",
            "Data": [
                1912,
                1912,
                1912,
                1913,
                1913
            ]
        },
        "Pseudo-Population": {
            "Units": "",
            "Data": [
                10000,
                10000,
                10000,
                10000,
                10000
            ]
        },
        "Statistical Population": {
            "Units": "",
            "Data": [
                10000,
                10000,
                10000,
                10000,
                10000
            ]
        }
    }
}
```
