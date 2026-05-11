# ReportMalariaFiltered


The malaria filtered report (ReportMalariaFiltered.json) is the same as the default InsetChart
report, but provides filtering options to enable the user to select the data to be displayed for
each time step or for each node. See [InsetChart report](software-report-inset-chart.md) for more information about
InsetChart.json.



## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

{{ read_csv('../csv/report-filtered-malaria.csv', keep_default_na=False) }}

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
            "Has_Interventions": ["SimpleVaccine", "IRSHousingModification"],
            "Include_30Day_Avg_Infection_Duration": 1
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data


This report produces the same output file format and channels as [InsetChart report](software-report-inset-chart.md).
See that page for a full description of the file structure and channel definitions.