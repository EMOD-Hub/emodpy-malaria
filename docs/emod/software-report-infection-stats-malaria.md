# ReportInfectionStatsMalaria


The malaria infection statistics report (ReportInfectionStatsMalaria.csv) provides per-infection
parasite burden data for every active infection in the simulation at each reporting interval. For
each infection it records the individual's identity and demographics, the infectiousness of the
individual, the current age of the infection, and — depending on configuration — the counts of
hepatocytes, infected red blood cells (IRBCs), and gametocytes associated with that infection.
Because the report produces one row per active infection per individual per reporting interval, the
output can be large; use **Start_Day**, **End_Day**, and **Reporting_Interval** to limit its size.

This report is only available for `MALARIA_SIM` simulations.


## Configuration


To generate this report, configure the following parameters in the custom_reports.json file:

```
**Filename_Suffix**, string, NA, NA, (empty string), "Suffix appended to the report filename. Required when configuring multiple instances of this report to prevent them from overwriting each other."
**Start_Day**, float, 0, 3.40E+38, 0, "The day of the simulation to start collecting data."
**End_Day**, float, 0, 3.40E+38, 3.40E+38, "The day of the simulation to stop collecting data."
**Reporting_Interval**, float, 1, 1000000, 1, "The number of time steps between data collection periods. Increasing this value reduces output file size."
**Include_Column_Hepatocyte**, boolean, NA, NA, 1, "If set to true (1), a column is added to the report with the count of infected hepatocytes for the infection."
**Include_Column_IRBC**, boolean, NA, NA, 1, "If set to true (1), a column is added to the report with the number of infected red blood cells (IRBCs) for the infection."
**Include_Column_Gametocyte**, boolean, NA, NA, 1, "If set to true (1), a column is added to the report with the total number of mature gametocytes (male and female combined) for the infection."
**Include_Data_Threshold_Hepatocytes**, float, 0, 3.40E+38, 0, "Minimum hepatocyte count an infection must have for its row to be written. Only applies when **Include_Column_Hepatocyte** is true. A value of 0 disables this threshold. If this threshold is not met, the entire row is omitted even if other thresholds are met."
**Include_Data_Threshold_IRBC**, float, 0, 3.40E+38, 0, "Minimum IRBC count an infection must have for its row to be written. Only applies when **Include_Column_IRBC** is true. A value of 0 disables this threshold. If this threshold is not met, the entire row is omitted even if other thresholds are met."
**Include_Data_Threshold_Gametocytes**, float, 0, 3.40E+38, 0, "Minimum gametocyte count an infection must have for its row to be written. Only applies when **Include_Column_Gametocyte** is true. A value of 0 disables this threshold. If this threshold is not met, the entire row is omitted even if other thresholds are met."
```

!!! note
    A row is only written if every enabled column meets its corresponding threshold. If any
    enabled threshold is not met, the entire row is omitted.

[link](../json/software-report-infection-stats-malaria.json)

## Output file data


The output file is named `ReportInfectionStatsMalaria.csv`. The report contains the following
columns.

```
Time, float, "The simulation time in days when the data was collected."
NodeID, integer, "The external ID of the node where the individual is currently present."
IndividualID, integer, "The unique ID of the individual carrying the infection."
Gender, enum, "The gender of the individual. Possible values are M or F."
AgeYears, float, "The age of the individual in years at the time of data collection."
InfectionID, integer, "The unique ID of the infection."
Infectiousness, float, "The infectiousness of the individual — the probability that a feeding mosquito will become infected. This value is based on the total number of gametocytes in the bloodstream contributed by all of the individual's infections."
Duration, float, "The duration in days of this infection at the time of data collection."
Hepatocytes, integer, "The number of infected hepatocytes associated with this infection. Only present if **Include_Column_Hepatocyte** is true."
IRBCs, integer, "The number of infected red blood cells associated with this infection. Only present if **Include_Column_IRBC** is true."
Gametocytes, integer, "The total number of mature gametocytes (male and female combined) associated with this infection. Only present if **Include_Column_Gametocyte** is true."
```

## Example


The following is an example of ReportInfectionStatsMalaria.csv.

{{ read_csv("csv/report-infection-stats-malaria.csv") }}
