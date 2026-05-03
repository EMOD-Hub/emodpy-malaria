# MalariaSurveyJSONAnalyzer


The malaria survey report (MalariaSurveyJSONAnalyzer.json) is a JSON-formatted report that provides
detailed information on an individual for each event that occurs during the reporting interval.
Multiple files can be created for each reporting interval.




## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
**Filename_Suffix**, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
**Start_Day**,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
**End_Day**,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data.  Empty list implies all nodes."
**Node_IDs_Of_Interest**,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list."
**Min_Age_Years**,"float","0","9.3228e+35","0","Minimum age in years of people to collect data on."
**Max_Age_Years**,"float","0","9.3228e+35","9.3228e+35","Maximum age in years of people to collect data on."
**Must_Have_IP_Key_Value**, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
**Must_Have_Intervention**, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
**Event_Trigger_List**, list of strings, NA, NA, NA, The list of event triggers for the events included in the report.
**Reporting_Interval**, integer, 1, 1000000, 1000000, "Defines the cadence of the report by specifying how many time steps to collect data before writing to the file. This will limit system memory usage and is advised when large output files are expected."
**Max_Number_Reports**, integer, 0, 1000000, 1, The maximum number of report output files that will be produced for a given campaign.
**Pretty_Format**, boolean, 0, 1, 0, "True (1) sets pretty JSON formatting. The default, false (0), saves space."
**IP_Key_To_Collect**, string, NA, NA, (empty string), "The name of the IndividualProperty Key whose value to collect; an empty string means collect values for all IPs."
```

[link](../json/software-report-malaria-survey-1.json)

## Output file data


The report contains the following information:

```
ntsteps, integer, "The number of days of the simulation for which data was collected. It equals the reporting interval unless the simulation ended before the reporting interval."
patient_array, array of strings, "An array where there is an entry for each individual that experiences the specified event(s) during the reporting interval. If no events are listed, an exception is thrown. The data in a patient array contain two types of data: data that has one value for each timestep or day and data that is an array of data."
```

### Patient_array channels


```
id, string, The individual ID of the person.
node_id, string, The External ID of the node that the person is currently in on the first event.
initial_age, float, "The initial age of the person (in days) when the report started tracking them.  This value will be non-zero for individuals created at initialization, but should be zero for the rest of the population."
local_birthday, float, "The day that the individual was born/created, in relation to the start of the report."
```

Each of the following statistics is presented as an array, where each entry is the value of that field
at the time of the event.

```
strain_ids, The antigen/clade ID and the genome ID of the individual's current infection.
ip_data, "If an **IP_Key_To_Collec**' was specified, this will be that value. If it was not specified, this will show the value for all of the IPs."
true_asexual_parasites, The actual parasite density of the individual.
true_gametocytes, The actual gametocyte density of the individual.
smeared_true_asexual_parasites, "The actual parasite density, smeared using NASBADensityWithUncertainty."
smeared_true_gametocytes, "The actual gametocyte density, smeared using NASBADensityWithUncertainty."
asexual_parasites, The parasite density measured using the BLOOD_SMEAR_PARASITES diagnostic.
gametocytes, The gametocyte density measured using the BLOOD_SMEAR_GAMETOCYTES diagnostic.
pcr_parasites, The parasite density measured using the PCR_PARASITES diagnostic.
pcr_gametocytes, The gametocyte density measured using the PCR_GAMETOCYTES diagnostic.
pfhrp2, The HRP2 measured using the PF_HRP2 diagnostic.
smeared_asexual_parasites, Positive fields of view (pos_asexual_fields) with parasite density.
smeared_gametocytes, Positive fields of view (pos_gametocyte_fields) with gametocyte density.
infectiousness, Infectious of the individual at the time of the event.
infectiousness_smeared, Binomial infectiousness smearing.
infectiousness_age_scaled, Infectiousness adjusted for age dependent Surface Area Biting.
pos_asexual_fields, The number of positive fields of view for parasite smears.
pos_gametocyte_fields, The number of positive fields of view for gametocyte smears.
temps, "The individual's body temperature in Celsius if they have a fever, otherwise it is -1."
```

## Example


The following is a sample of a MalariaSurveyJSONAnalyzer file.

[link](../json/software-report-malaria-survey-2.json)
