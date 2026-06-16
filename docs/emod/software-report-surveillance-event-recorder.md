# ReportSurveillanceEventRecorder


The surveillance event recorder report (ReportSurveillanceEventRecorder.csv) is a CSV report that
logs detailed information each time a
[SurveillanceEventCoordinator](parameter-campaign-event-coordinators.md#surveillanceeventcoordinator)
responds to what it is observing. It extends
the coordinator event recorder by adding surveillance-specific data: the count of events observed
during the counting period, the threshold that triggered the response, and population statistics for
the nodes visible to the coordinator.

This report only records events from coordinators that implement the surveillance reporting
interface (i.e., **SurveillanceEventCoordinator**). Coordinator-level events from other event
coordinators are ignored. For recording events from all coordinator types, see
ReportCoordinatorEventRecorder.

When the surveillance coordinator finishes a counting period and the accumulated count meets a
threshold defined in the responder's action list, the responder broadcasts an action event (and
optionally a responded event). This report captures that moment: the event name, how many
incidences were counted, which threshold was crossed, and how many individuals in the coordinator's
node set match its demographic restrictions.

Optionally, you can break down the population statistics by individual property (IP) values using
**Report_Surveillance_Event_Recorder_Stats_By_IPs**. For each IP key listed, the report adds two
columns per key-value pair showing the number of qualifying individuals and the number of infected
individuals with that property value.


## Configuration


To generate this report, the following parameters must be configured in the config.json file:

{{ read_csv('../csv/report-surveillance-event-recorder.csv', keep_default_na=False) }}

```json
{
    "Report_Surveillance_Event_Recorder": 1,
    "Report_Surveillance_Event_Recorder_Events": [],
    "Report_Surveillance_Event_Recorder_Ignore_Events_In_List": 1,
    "Report_Surveillance_Event_Recorder_Stats_By_IPs": ["Risk"]
}
```


## Output file data


The report (ReportSurveillanceEventRecorder.csv) contains one row per surveillance response event.
The columns are described below.

### Base columns

These columns are inherited from the coordinator event recorder and are always present.

| Data channel | Data type | Description |
| --- | --- | --- |
| `Time` | float | The simulation time (in days) when the surveillance coordinator responded. |
| `Coordinator_Name` | string | The name of the surveillance event coordinator, as set by the **Coordinator_Name** parameter in the campaign. Useful for distinguishing between multiple surveillance coordinators. |
| `Event_Name` | string | The coordinator-level event that was broadcast by the responder. This is one of the events defined in the responder's action list, or the **Responded_Event** if configured. If **Report_Surveillance_Event_Recorder_Ignore_Events_In_List** is set to 0, only events listed in **Report_Surveillance_Event_Recorder_Events** appear. |

### Surveillance columns

These columns provide data about the surveillance coordinator's counting and response decision.

| Data channel | Data type | Description |
| --- | --- | --- |
| `NumCounted` | integer | The number of events (incidences) counted by the **IncidenceCounterSurveillance** during the most recent counting period. This is the raw count of trigger events that occurred and matched the counter's demographic and property restrictions. |
| `ThresholdOfAction` | float | The threshold value from the responder's action list that was met or exceeded, causing the response. When **Threshold_Type** is ``COUNT``, this is a raw count. When it is ``PERCENTAGE`` or ``PERCENTAGE_EVENTS``, this is a fraction. |

### Population statistics columns

These columns summarize the population visible to the coordinator at the time of the response.
The counts reflect individuals in the coordinator's node set who meet any demographic coverage
and property restrictions configured on the **IncidenceCounterSurveillance**.

| Data channel | Data type | Description |
| --- | --- | --- |
| `NumIndividuals` | integer | The total number of qualifying individuals across all nodes assigned to the coordinator. |
| `NumInfected` | integer | The number of qualifying individuals who are currently infected. |

### Individual property (IP) breakdown columns

If **Report_Surveillance_Event_Recorder_Stats_By_IPs** is configured with one or more IP key
names, additional column pairs are appended for each key-value combination defined in the
demographics file. For example, if ``Risk`` has values ``HIGH`` and ``LOW``, the following columns
are added:

| Data channel | Data type | Description |
| --- | --- | --- |
| `Risk:HIGH:NumIndividuals` | integer | The number of qualifying individuals whose ``Risk`` property is ``HIGH``. |
| `Risk:HIGH:NumInfected` | integer | The number of infected qualifying individuals whose ``Risk`` property is ``HIGH``. |
| `Risk:LOW:NumIndividuals` | integer | The number of qualifying individuals whose ``Risk`` property is ``LOW``. |
| `Risk:LOW:NumInfected` | integer | The number of infected qualifying individuals whose ``Risk`` property is ``LOW``. |

The column naming convention is ``<Key>:<Value>:NumIndividuals`` and ``<Key>:<Value>:NumInfected``
for each IP key-value pair.


## Example


The following is an example of a ReportSurveillanceEventRecorder.csv report. In this example, a
**SurveillanceEventCoordinator** named ``ACF_Counter`` is counting ``NewClinicalCase`` events in
30-day periods and responding when the count exceeds a threshold of 2. The ``Risk`` individual
property is tracked via **Report_Surveillance_Event_Recorder_Stats_By_IPs**.

| Time | Coordinator_Name | Event_Name | NumCounted | ThresholdOfAction | NumIndividuals | NumInfected | Risk:HIGH:NumIndividuals | Risk:HIGH:NumInfected | Risk:LOW:NumIndividuals | Risk:LOW:NumInfected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30 | ACF_Counter | Respond_To_Surveillance | 5 | 2 | 1000 | 120 | 300 | 55 | 700 | 65 |
| 60 | ACF_Counter | Respond_To_Surveillance | 3 | 2 | 998 | 85 | 299 | 30 | 699 | 55 |
| 90 | ACF_Counter | Respond_To_Surveillance | 8 | 2 | 995 | 210 | 298 | 95 | 697 | 115 |
