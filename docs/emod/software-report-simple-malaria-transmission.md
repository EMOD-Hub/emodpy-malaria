# ReportSimpleMalariaTransmission


The simple malaria transmission report (ReportSimpleMalariaTransmission.csv) is a
CSV-formatted report that provides data on malaria transmission, by tracking who transmitted
malaria to whom. The report can only be used when the simulation setup parameter **Malaria_Model** is
set to MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION. This report is typically used as input to the
GenEpi model. See the [output](#output-file-data) section for more details.

..To do: need section on co-transmission!


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
**Pretty_Format**, boolean, 0, 1, 0, "True (1) sets pretty JSON formatting. The default, false (0), saves space."
**Start_Day**, float, 0,  3.40E+38, 0, The day to start collecting data for the report.
**Include_Human_To_Vector_Transmission**, boolean, NA, NA, 0, "If set to true (1), Human-to-Vector transmission events will be included. One can identify these events because the 'acquireIndividualId'=0 and transmitTime=acquireTime. WARNING: This can make the file size quite large."
```

[link](../json/software-report-simple-malaria-transmission-1.json)


## Output file data


The report contains transmissions as an array of CoTransmission objects that contain data on where
the infection came from. Each object represents a new infection in the specified node. The following
is the structure of a CoTransmission object:


```
acquireIndividualId, integer, The ID of the individual who received an infection from the vector.
acquireInfectionIds, integer, "The list of infections created due to a bite from the vector. There is only one entry in this list at this time."
acquireTime, integer, "The day the vector infected the individual with acquireIndividualId."
concurrentInfectionIds, array of integers, "The IDs of other infections the acquiring individual had when they were infected with this new infection."
node_id, integer, The ID of the node where the infection occurred.
transmitTime, integer, "The day when the vector was infected. Can be 0 if the infection was due to OutbreakIndividual."
transmitIndividualId, integer, "The ID of the individual that infected the vector. Can be 0 if the infection was due to OutbreakIndividual."
transmitInfectionIds, array of integers, "The list of infection IDs of the individuals infecting the vectors. Can be empty if the infection was due to OutbreakIndividual."
transmitGametocyteDensities, array of floats, "A parallel list to transmitInfectionIds where each gametocyte density is the density for the corresponding infection. Can be empty if the infection was due to OutbreakIndividual."
vectorId, integer, "The ID of the vector that was infected by the transmitIndividualId and who gave it to the acquireIndividualId. Can be 0 if the infection was due to OutbreakIndividual."
```

## Example


The following is an example of a ReportSimpleMalariaTransmission file.

[link](../json/software-report-simple-malaria-transmission-2.json)
