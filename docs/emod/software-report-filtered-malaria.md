# ReportMalariaFiltered


The malaria filtered report (ReportMalariaFiltered.json) is the same as the default InsetChart
report, but provides filtering options to enable the user to select the data to be displayed for
each time step or for each node. See [software-report-inset-chart](software-report-inset-chart.md) for more information about
InsetChart.json.



## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
**Filename_Suffix**, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
**Start_Day**,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
**End_Day**,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
**Node_IDs_Of_Interest**,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list.  Empty list implies all nodes."
**Min_Age_Years**,"float","0","9.3228e+35","0","Minimum age in years of people to collect data on."
**Max_Age_Years**,"float","0","9.3228e+35","9.3228e+35","Maximum age in years of people to collect data on."
**Must_Have_IP_Key_Value**, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
**Must_Have_Intervention**, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
**Has_Interventions**, array of strings, NA, NA, [ ], "A channel is added to the report for each InterventionName you specify in the campaign file. In the InsetChart report, the channel name is Has _ and is the fraction of the population that has that intervention. The **Intervention_Name** values in the campaign should be the values in this parameter."
**Include_30Day_Avg_Infection_Duration**, boolean, NA, NA, 1, "If set to true (1), the 30-Day Avg Infection channel is included in the report."
```

```json
{
    "Reports": [
        {
            "class": "ReportMalariaFiltered",
            "Filename_Suffix": "AllNodes",
            "Start_Day": 365,
            "End_Day": 1000,
            "Node_IDs_Of_Interest": [],
            "Min_Age_Years": 5,
            "Max_Age_Years": 10,
            "Must_Have_IP_Key_Value": "Risk:HIGH",
            "Must_Have_Intervention": "UsageDependentBednet",
            "Has_Interventions": ["SimpleVaccine","IRSHousingModification"],
            "Include_30Day_Avg_Infection_Duration": 1
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data


This report produces the same output file format and channels as [software-report-inset-chart](software-report-inset-chart.md).
See that page for a full description of the file structure and channel definitions.