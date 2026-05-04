# ReportNodeDemographicsMalaria


The malaria node demographics report is a CSV-formatted report that extends the ReportNodeDemographics
report (see [software-report-node-demographics](software-report-node-demographics.md)) by adding malaria-specific statistics. The
report still contains population information stratified by node, but the data columns now also
contain information about malaria parasite counts.



## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
**Age_Bins**, array of floats, -3.04E+38, 3.04E+38, [ ], "The age bins (in years, in ascending order) to aggregate within and report. An empty array does not stratify by age."
**IP_Key_To_Collect**, string, NA, NA, (empty string), "The name of the **IndividualProperties** (IP) key by which to stratify the report. An empty string means the report is not stratified by IP."
**Stratify_By_Gender**, boolean, 0, 1, 1, "Set to true (1) to stratify by gender; a value of 0 will not stratify by gender."
**Stratify_By_Has_Clinical_Symptoms**, bool, NA, NA, 1, "If set to 1, the data will have an extra stratification for people who have clinical symptoms and those that do not.  Default is 0 or no extra stratification."
```

[link](../json/software-report-malaria-node-demographics.json)

## Output file data


The report will contain the following output data, divided between stratification columns and data
columns.


### Stratification columns


```
Time, float, The day of the simulation that the data was collected.
NodeID, integer, The External ID of the node for the data in the row in the report.
Gender, enum, "Possible values are M or F; the gender of the individuals in the row in the report.  This column only appears if **Stratify_By_Gender** = 1."
AgeYears, float, "The max age in years of the bin for the individuals in the row in the report.  If **Age_Bins** is empty, this column does not appear."
IndividualProp, string, "The value of the IP for the individuals in the row in the report.  If **IP_Key_To_Collect** is an empty string, then this column does not appear."
HasClinicalSymptoms, enum, "T implies that the people in the row are having clinical symptoms.  F implies they do not.  This column only appears if **Stratify_By_Has_Clinical_Symptoms** = 1."
```

### Data columns


```
NumIndividuals, integer, The number of individuals that meet the stratification values.
NumInfected, integer, The number of infected individuals that meet the stratification values.
NodeProp = <Node Property Keys>, string, "For each possible Node Property, there is one column where the data in the column is the value of that particular property. If there are no **NodeProperties**, then there are no columns."
AvgInfectiousness, float, "The average infectiousness to mosquitos for the individuals of this row.  Infectiousness is based on the number of mature gametocytes that the person has."
AvgParasiteDensity, float, The average true parasite density for the individuals of this row.
AvgGametocyteDensity, float, The average true gametocyte density for the individuals of this row.
AvgVariantFractionPfEMP1Major, float, "For each individual, a count is made of the number of PfEMP1 Major antibodies the individual has and is divided by the total number of possible variants (Falciparum_PfEMP1_Variants). This is the average of this value for all the individuals represented in this row."
AvgNumInfections, float, The average number of infections for the people of this row.
AvgInfectionClearedDuration, float, The average duration to clear infections for the people of this row.
NumInfectionsCleared, integer, The number of cleared infections for the people of this row.
NumHasFever, integer, "The number of people in the row that have a fever according to the diagnostic using the **Report_Detection_Threshold_Fever** parameter."
NumHasClinicalSymptoms, integer, "If **Stratify_By_Has_Clinical_Symptoms** = 0, then this column is present with the number of people in the row that are considered to have 'clinical' symptoms."
```

## Example


The following is an example of ReportNodeDemographicsMalaria.csv.

```
50,1,M,10, arm1, F,366,0,0,0,0,0,0,0,0,0
50,1,M,10, arm1, T,151,151,0.00593093,112435,1.06936,0.0165342,1,0,0,151
50,1,M,10, arm2, F,1256,0,0,0,0,0,0,0,0,0
50,1,M,10, arm2, T,292,292,0.00615811,111366,1.11031,0.0165525,1,0,0,292
50,1,M,10, arm3, F,2744,0,0,0,0,0,0,0,0,0
50,1,M,10, arm3, T,282,282,0.00600333,111783,1.08239,0.0165839,1,0,0,282
50,1,M,100, arm1, F,335,0,0,0,0,0,0,0,0,0
50,1,M,100, arm1, T,159,159,0.00205596,140531,0.371012,0.0166038,1,0,0,159
50,1,M,100, arm2, F,946,0,0,0,0,0,0,0,0,0
50,1,M,100, arm2, T,588,588,0.00205613,140583,0.371029,0.0165647,1,0,0,588
50,1,M,100, arm3, F,2645,0,0,0,0,0,0,0,0,0
50,1,M,100, arm3, T,297,297,0.00205629,140105,0.371017,0.0165545,1,0,0,297
50,1,F,10, arm1, F,379,0,0,0,0,0,0,0,0,0
50,1,F,10, arm1, T,164,164,0.00606003,110326,1.09222,0.0165447,1,0,0,164
50,1,F,10, arm2, F,1143,0,0,0,0,0,0,0,0,0
50,1,F,10, arm2, T,288,288,0.00595153,111696,1.07296,0.0165162,1,0,0,288
50,1,F,10, arm3, F,2809,0,0,0,0,0,0,0,0,0
50,1,F,10, arm3, T,302,302,0.00597365,111095,1.07672,0.0165011,1,0,0,302
50,1,F,100, arm1, F,355,0,0,0,0,0,0,0,0,0
50,1,F,100, arm1, T,144,144,0.00205568,141105,0.37102,0.0166435,1,0,0,144
50,1,F,100, arm2, F,887,0,0,0,0,0,0,0,0,0
50,1,F,100, arm2, T,579,579,0.00205593,140874,0.371017,0.0165688,1,0,0,579
50,1,F,100, arm3, F,2584,0,0,0,0,0,0,0,0,0
50,1,F,100, arm3, T,305,305,0.00205636,140043,0.371022,0.0165465,1,0,0,305
50,2,M,10, arm1, F,340,0,0,0,0,0,0,0,0,0
50,2,M,10, arm1, T,147,147,0.00608663,112032,1.09768,0.016644,1,0,0,147
50,2,M,10, arm2, F,1161,0,0,0,0,0,0,0,0,0
50,2,M,10, arm2, T,311,311,0.00599196,111639,1.08021,0.0165274,1,0,0,311
50,2,M,10, arm3, F,2742,0,0,0,0,0,0,0,0,0
50,2,M,10, arm3, T,285,285,0.00596162,112175,1.07493,0.0165731,1,0,0,285
50,2,M,100, arm1, F,327,0,0,0,0,0,0,0,0,0
50,2,M,100, arm1, T,160,160,0.0020567,139714,0.371016,0.0164792,1,0,0,160
50,2,M,100, arm2, F,899,0,0,0,0,0,0,0,0,0
50,2,M,100, arm2, T,583,583,0.00205599,140620,0.371006,0.0165638,1,0,0,583
50,2,M,100, arm3, F,2697,0,0,0,0,0,0,0,0,0
50,2,M,100, arm3, T,278,278,0.00205585,141016,0.371021,0.0165828,1,0,0,278
50,2,F,10, arm1, F,332,0,0,0,0,0,0,0,0,0
50,2,F,10, arm1, T,160,160,0.00600168,112563,1.08236,0.0166042,1,0,0,160
50,2,F,10, arm2, F,1184,0,0,0,0,0,0,0,0,0
50,2,F,10, arm2, T,333,333,0.00607677,111940,1.09565,0.0165566,1,0,0,333
50,2,F,10, arm3, F,2731,0,0,0,0,0,0,0,0,0
50,2,F,10, arm3, T,294,294,0.00601945,111251,1.08511,0.0165306,1,0,0,294
50,2,F,100, arm1, F,341,0,0,0,0,0,0,0,0,0
50,2,F,100, arm1, T,156,156,0.00205657,139663,0.371027,0.0165171,1,0,0,156
50,2,F,100, arm2, F,914,0,0,0,0,0,0,0,0,0
50,2,F,100, arm2, T,626,626,0.00205598,140771,0.371019,0.0165549,1,0,0,626
50,2,F,100, arm3, F,2728,0,0,0,0,0,0,0,0,0
50,2,F,100, arm3, T,271,271,0.00205597,140890,0.370996,0.0165068,1,0,0,271
```
