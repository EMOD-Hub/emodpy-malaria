# ReportInfectionDuration


The infection duration report (ReportInfectionDuration.csv) records one row each time an infection
clears in an individual, capturing the identity and age of the individual, the node, and the total
duration of that infection in days. Because the report writes a row for every `InfectionCleared`
event, you may want to use **Start_Day** and **End_Day** to limit the output to the time window of
interest.


## Configuration


To generate this report, configure the following parameters in the custom_reports.json file:

```
**Start_Day**, float, 0, 3.40E+38, 0, "The day of the simulation to start collecting data."
**End_Day**, float, 0, 3.40E+38, 3.40E+38, "The day of the simulation to stop collecting data."
```

[link](../json/software-report-infection-duration.json)

## Output file data


The output file is named `ReportInfectionDuration.csv`. The report contains the following columns.

```
Time, float, "The simulation time in days when the infection was cleared."
NodeID, integer, "The external ID of the node where the individual resides."
IndividualID, integer, "The unique ID of the individual whose infection cleared."
Gender, enum, "The gender of the individual. Possible values are M or F."
AgeYears, float, "The age of the individual in years at the time the infection cleared."
InfectionDuration, float, "The duration in days of the infection that cleared."
```

## Example


The following is an example of ReportInfectionDuration.csv.

{{ read_csv("csv/report-infection-duration.csv") }}
