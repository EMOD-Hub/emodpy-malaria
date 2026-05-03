# ReportEventRecorder


The health events and interventions report (ReportEventRecorder.csv) provides information on each
individual's demographics and health status at the time of an event. Additionally, it is possible to
see the value of specific **IndividualProperties**, as assigned in the demographics file (see
[NodeProperties and IndividualProperties](parameter-demographics.md:nodeproperties-and-individualproperties) for more information).

This report is highly customizable; see the Configuration section, below, for details and instructions.
Disease-specific information and examples are provided at the end of page.


## Configuration


To generate this report, the following parameters must be configured in the config.json file (applies
to all simulation types):


```
Report_Event_Recorder,"boolean","0","1","0","Set to 1 to generate the report."
Report_Event_Recorder_Events,"array of strings","NA","NA","[]","The list of events to include or exclude in the output report, based on how **Report_Event_Recorder_Ignore_Events_In_List** is set. See :doc:`parameter-campaign-event-list` for a list of all possible built-in events. **Custom_Individual_Events** may also be included. Warning: If the list is empty and **Report_Event_Recorder_Ignore_Events_In_List** is set to 0, no events will be returned."
Report_Event_Recorder_Ignore_Events_In_List,"boolean","0","1","0","If set to false (0), only the events listed in **Report_Event_Recorder_Events** will be included in the output report. If set to true (1), only the events listed in **Report_Event_Recorder_Events** will be excluded, and all other events will be included. To return all events from the simulation, set this value to 1 and leave the the **Report_Event_Recorder_Events** array empty."
Report_Event_Recorder_Individual_Properties,"array of strings","NA","NA","[]","An array of optional individual property (IP) keys to be added to the report. One column will be added for each IP Key listed, indicating the individual's value for that IP Key at the time of the event. See :doc:`model-properties` for details on setting individual properties."
Report_Event_Recorder_Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
Report_Event_Recorder_End_Day,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
Report_Event_Recorder_Node_IDs_Of_Interest,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list. Leave the array empty (default value) to collect data on all nodes."
Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest, string, NA, NA, \"\", "If the string is not empty, then the recorder will add the PropertyChange event to the list of events that the report is listening to. However, it will only record the events where the property changed the value of the given key."
Report_Event_Recorder_Min_Age_Years,"float","0","9.3228e+35","0","Minimum age in years of people to collect data on."
Report_Event_Recorder_Max_Age_Years,"float","0","9.3228e+35","9.3228e+35","Maximum age in years of people to collect data on."
Report_Event_Recorder_Must_Have_IP_Key_Value,"string","NA","NA",\"\","An individual property (IP) Key:Value pair that an individual must have in order to be included in the report. Leave the string empty (default value) to not include IPs in the selection criteria. See :doc:`model-properties` for more information."
Report_Event_Recorder_Must_Have_Intervention,"string","NA","NA",\"\","The name of the intervention that the individual must have in order to be included in the report. Leave the string empty (default value) to not include interventions in the selection criteria. See :doc:`parameter-campaign-individual-interventions` for more information."
```

```json
{
    "Report_Event_Recorder": 1,
    "Report_Event_Recorder_Events": [],
    "Report_Event_Recorder_Ignore_Events_In_List": 1,
    "Report_Event_Recorder_Individual_Properties": ["Risk"],
    "Report_Event_Recorder_Start_Day": 1,
    "Report_Event_Recorder_End_Day": 300,
    "Report_Event_Recorder_Node_IDs_Of_Interest": [ 1, 2, 3 ],
    "Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest": "",
    "Report_Event_Recorder_Min_Age_Years": 20,
    "Report_Event_Recorder_Max_Age_Years": 60,
    "Report_Event_Recorder_Must_Have_IP_Key_Value": "Risk:HIGH",
    "Report_Event_Recorder_Must_Have_Intervention": "",
}
```

## Output file data


The report contains the following data channels for malaria simulations.

```
Time, float, "The time of the event, in days."
Node_ID, integer, "The identification number of the node."
Event_Name, string, "The event being logged. If **Report_Event_Recorder_Ignore_Events_In_List** is set to 0, then the event name will be one of the ones listed under **Report_Event_Recorder_Events**. Otherwise, it will be the name of any other event that occurs and is not listed under **Report_Event_Recorder_Events**."
Individual_ID, integer, The individual's unique identifying number
Age, integer, "The age of the individual in units of days. Divide by 365 to obtain age in years."
Gender, character, "The gender of the individual: ""M"" for male, or ""F"" for female."
Infected, boolean, "Describes whether the individual is infected or not; 0 when not infected, 1 for infected."
Infectiousness, float, "A value ranging from 0 to 1 that indicates how infectious an individual is, with 0 = not infectious and 1 = very infectious. HIV and malaria simulation types have specific definitions listed below."
"<IP Key>", string, "An additional column will be added to the report for each IP Key listed in **Report_Event_Recorder_Individual_Properties**. The values shown in each column will be the value for the indicated key, for that individual, at the time of the event."
RelativeBitingRate, float, "A number indicating the likelihood of an individual being bitten by mosquitoes. This can include any biting rates set by the user and/or a value based on the age or size of the individual."
HasClinicalSymptoms, T/F, "T implies that the person's fever has been above **Clinical_Fever_Threshold_Low** for at least **Min_Days_Between_Clinical_Incidents** since the person was a NewClinicalCase (their fever first peaked above **Clinical_Fever_Threshold_High**), F implies that the person is not considered to have clinical symptoms."
TrueParasiteDensity, float, The number of infected red blood cells per microliter of blood.
TrueGametocyteDensity, float, The true number of gametocytes per microliter of blood.
```

## Example


The following is an example of a ReportEventRecorder.csv report from a malaria simulation:

```
30,7,EveryUpdate,15,4797.43,M,1,0,1,19791.2,0,T
35,7,EveryUpdate,1037,642.683,F,1,0.227641,1,644.143,42.5087,F
35,7,EveryUpdate,1058,12432.7,F,1,0.036678,1,970.459,7.63285,F
35,7,EveryUpdate,1065,14232.2,F,1,0.006245,1,110913,7.63259,T
35,7,EveryUpdate,1093,19206.8,F,1,0.035739,1,1020.28,7.63263,F
35,7,EveryUpdate,1114,17144.3,M,1,0.006236,1,73854.4,7.63208,T
35,7,EveryUpdate,1135,5739.73,F,1,0.007743,1,106963,9.4479,T
35,7,EveryUpdate,1149,6064.07,F,1,0.044953,1,1138.48,9.00229,F
35,7,EveryUpdate,1163,21692.3,M,1,0.006216,1,118332,7.63267,T
35,7,EveryUpdate,1170,14238.3,F,1,0.006216,1,118332,7.6325,T
35,7,EveryUpdate,6924,7388.82,F,1,0.03641,1,1248.47,7.63267,F
35,7,EveryUpdate,6938,20377.8,F,1,0.006216,1,118331,7.63272,T
35,7,EveryUpdate,6952,29412.4,M,1,0.006216,1,118333,7.63291,T
35,7,EveryUpdate,6959,32766.3,M,1,0.037062,1,952.578,7.63273,F
35,7,EveryUpdate,6966,1245.33,F,1,0.025033,1,64225.2,30.0704,T
35,7,EveryUpdate,6994,13428.8,F,1,0.006236,1,113029,7.63279,T
40,7,EveryUpdate,15,4807.43,M,1,1,1,14.8706,940.014,F
```
