# ReportDrugStatus



The drug status report (ReportDrugStatus.csv) provides status information on the drugs that an
individual has taken or is waiting to take. Because the report provides information for each drug,
for each individual, and for each time step, you may want to use the **Start_Day** and **End_Day**
parameters to limit the size of the output file. You cannot filter based on the demographics parameter
**IndividualProperties**.



## Configuration


To generate this report, configure the following parameters in the custom_report.json file:

```
**End_Day**, float, 0, 3.40E+38, 3.40E+38, "The day to stop collecting data for the report."
**Start_Day**, float, 0, 3.40E+38, 0, The day to start collecting data for the report.
```

```json
{
    "Reports": [
        {
            "Start_Day": 300,
            "End_Day": 900,
            "class": "ReportDrugStatus"
        }
    ],
    "Use_Defaults": 1
}
```

## Output data


The report contains the following stratification columns:

```
Time, integer, The day of the simulation on which the data was collected for the data in the row.
NodeID, string, The external ID of the node.
```

The report contains the following data columns:

```
IndividualID, integer, The ID of the individual who received the drug.
Gender, enum, "The gender of the individual. Possible values are M or F."
AgeYears, integer, The max age in years of the age bin for the individual.
Infected, boolean, "A true value (1) indicates the individual is infected and a false value (0) indicates the individual is not infected."
Infectiousness, float, "A value from 0 to 1 that indicates how infectious an individual is, with 0 = not infectious and 1 = very infectious. This is the probability that an individual will infect a mosquito during a successful blood meal."
DrugName, string, "The name of the drug indicated in the intervention (**Malaria_Drug_Params** in config.json). Depending on the intervention, this might be a concatenated value when an individual takes multiple pills in one dose."
CurrentEfficacy, float, "The current efficacy of the drug(s). The efficacy is determined by the selected PKPD model; see :doc:`malaria-model-antimalarial-drugs` for more information."
NumRemainingDoses, integer, The number of remaining doses the individual will receive.
```

## Example


The following is an example of ReportDrugStatus.csv.

{{ read_csv("csv/report-malaria-drug-status.csv") }}
