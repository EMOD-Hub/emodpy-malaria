# MalariaPatientJSONReport


The malaria patient data report (MalariaPatientJSONReport.json)  is a JSON-formatted report that
provides medical data for each individual on each day of the simulation. For example, for a
specified number of time steps, each "patient" will have information collected on the temperature of
their fever, their parasite counts, treatments they received, and other relevant data.



## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
Filename_Suffix, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
End_Day,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
Node_IDs_Of_Interest,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list.  Empty list implies all nodes."
Min_Age_Years,"float","0","9.3228e+35","0","Minimum age in years of people to collect data on."
Max_Age_Years,"float","0","9.3228e+35","9.3228e+35","Maximum age in years of people to collect data on."
Must_Have_IP_Key_Value, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
Must_Have_Intervention, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
```

```json
{
    "Reports": [
        {
            "class": "MalariaPatientJSONReport",
            "Filename_Suffix": "Node1",
            "Start_Day": 365,
            "End_Day": 465,
            "Node_IDs_Of_Interest": [ 1 ],
            "Min_Age_Years": 5,
            "Max_Age_Years": 10,
            "Must_Have_IP_Key_Value": "Risk:LOW",
            "Must_Have_Intervention": "UsageDependentBednet"
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data


The report contains the following information:

```
ntsteps, integer, "Number of time steps in the simulation in which the report is active.  Each channel for each person has this number of elements People that are born after the start of the simulation or die before the end will have fewer entries."
patient_array, "array of JSON objects", "For each patient in patient_array, there will be a dictionary of key:value pairs. Some dictionary entries will contain a single, constant value that does not change through time, such as the individual’s birthday. Other dictionary entries will be arrays of daily measures for that individual, such as the count of count of asexual parasites on each day of the simulation. Please see the example below for an illustration."
```

### Patient data channels


Each of the following statistics has one value for each timestep or day.


```
id, string, The unique ID of the individual.
initial_age, float, "The initial age of the person, in days, when the report started tracking them.  This value will be non-zero for individuals created at initialization, but should be zero for the rest of the population."
birthday, float, The day that the individual was born/created in relation to the start of the report.
```

### Patient array data channels


Each of the following statistics is an array of data, where each entry is the value of that field at
the time of the event.


```
asexual_parasites, integer, The results of the BLOOD_SMEAR_PARASITES diagnostic that reports the number of parasites detected.
asexual_positive_fields, integer, The count of parasites using positive slide fields.
gametocyte_positive_fields, integer, The count of gametocytes using positive slide fields.
gametocytes, integer, The results of the BLOOD_SMEAR_GAMETOCYTES diagnostic that reports the number of gametocytes detected.
hemoglobin, float, The amount of hemoglobin the individual has based on their red blood cell count.
infected_mosquito_fraction, float, The fraction of mosquito bites  the patient received from infectious mosquitoes.
temps, float, "The individual's body temperature, in Celsius, when they had a fever. It is -1 if they do not have a fever.  This is based on their cytokine level."
treatment, string, "The list of drug names that the user is currently taking, which includes any drugs in the person's system during that timestep.  The names are separated by 'space+space.'"
true_asexual_parasites, float, The actual number of parasites that the individual has.
true_gametocytes, float, The actual number of gametocytes that the individual has.
```

## Example


The following is an example of MalariaPatientReport.json.

```json
{
    "ntsteps": 5,
    "patient_array": [{
        "asexual_parasites": [
            [
                0,
                30,
                30,
                730,
                570

            ]
        ],
        "asexual_positive_fields": [
            [
                0,
                21,
                19,
                154,
                147
            ]
        ],
        "birthday": -3031.024658203,
        "gametocyte_positive_fields": [
            [
                0,
                0,
                0,
                0,
                1
            ]
        ],
        "gametocytes": [
            [
                0,
                0,
                0,
                0,
                10
            ]
        ],
        "hemoglobin": [
            [
                13.95295619965,
                13.94942092896,
                13.94591999054,
                13.94245052338,
                13.93901348114
            ]
        ],
        "id": 1,
        "infected_mosquito_fraction": [
            [
                0,
                0.02632671967149,
                0.1359317451715,
                0.3907080292702,
                2.00230383873
            ]
        ],
        "initial_age": 3031.024658203,
        "temps": [
            [
                -1,
                38.39496612549,
                40.47192382813,
                40.53329849243,
                43.32601165771
            ]
        ],
        "treatment": [
            [
                "",
                "",
                "",
                "",
                ""
            ]
        ],
        "true_asexual_parasites": [
            [
                0,
                0.01264353003353,
                0.2007576525211,
                2.86963891983,
                41.02872848511
            ]
        ],
        "true_gametocytes": [
            [
                0,
                0.3181047737598,
                4.729532718658,
                67.70833587646,
                967.8447875977
            ]
        ]
    }]
}
```
