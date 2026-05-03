# ReportNodeDemographics


The node demographics report (ReportNodeDemographics.csv) is a CSV-formatted report that provides
population information stratified by node. For each time step, the report will collect data on each
node and age bin.


## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
**Age_Bins**, array of floats, -3.04E+38, 3.04E+38, [ ], "The age bins (in years, in ascending order) to aggregate within and report. An empty array does not stratify by age."
**IP_Key_To_Collect**, string, NA, NA, (empty string), "The name of the **IndividualProperties** (IP) key by which to stratify the report. An empty string means the report is not stratified by IP."
**Stratify_By_Gender**, boolean, NA, NA, 1, "Set to true (1) to stratify by gender; a value of 0 will not stratify by gender."
```

```json
{
    "Reports": [
        {
            "class": "ReportNodeDemographics",
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
            "IP_Key_To_Collect": "",
            "Stratify_by_Gender": 1
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data


The report will contain the following output data, divided between stratification columns and data
columns.

### Stratification columns


```
Time, float, The day of the simulation that the data was collected.
NodeID, integer, The external ID of the node for the data in the row in the report.
Gender, enum, "Possible values are M or F; the gender of the individuals in the row in the report.  This column only appears if **Stratify_By_Gender** = 1."
AgeYears, float, "The max age in years of the bin for the individuals in the row in the report.  If **Age_Bins** is empty, this column does not appear."
IndividualProp, string, "The value of the IP for the individuals in the row in the report.  If **IP_Key_To_Collect** is an empty string, then this column does not appear."
```

### Data columns


```
NumIndividuals, integer, The number of individuals that meet the stratification values.
NumInfected, integer, The number of infected individuals that meet the stratification values.
NodeProp = <Node Property Keys>, string, "For each possible Node Property, there is one column where the data in the column is the value of that particular property. If there are no Node Properties, then there are no columns."
```

## Example



The following is an example of ReportNodeDemographics.csv.

{{ read_csv("../csv/report-node-demographics.csv") }}
