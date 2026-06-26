# ReportCoordinatorEventRecorder


The coordinator event recorder report (ReportCoordinatorEventRecorder.csv) records coordinator-level
events that are broadcast during the simulation. It logs the event name, the time the event occurred,
and the name of the coordinator that broadcast it.

Coordinator-level events are typically broadcast by campaign classes such as
[BroadcastCoordinatorEvent](parameter-campaign-event-broadcastcoordinatorevent.md) and
[SurveillanceEventCoordinator](parameter-campaign-event-surveillanceeventcoordinator.md).

For recording individual-level events, see [ReportEventRecorder](software-report-event-recorder.md).
For node-level events, see [ReportNodeEventRecorder](software-report-node-event-recorder.md).
For surveillance-specific coordinator events with additional population statistics, see
[ReportSurveillanceEventRecorder](software-report-surveillance-event-recorder.md).


## Configuration


To generate this report, the following parameters must be configured in the config.json file:

{{ read_csv('../csv/report-coordinator-event-recorder.csv', keep_default_na=False) }}

```json
{
    "Report_Coordinator_Event_Recorder": 1,
    "Report_Coordinator_Event_Recorder_Events": ["VectorSurveyDone"],
    "Report_Coordinator_Event_Recorder_Ignore_Events_In_List": 0
}
```


## Output file data


The report (ReportCoordinatorEventRecorder.csv) contains one row per coordinator event. The columns
are described below.

| Data channel | Data type | Description |
| --- | --- | --- |
| `Time` | float | The simulation time (in days) when the coordinator event was broadcast. |
| `Coordinator_Name` | string | The name of the event coordinator that broadcast the event, as set by the **Coordinator_Name** parameter in the campaign definition. Useful for distinguishing between multiple coordinators that broadcast the same event. |
| `Event_Name` | string | The coordinator-level event that was broadcast. If **Report_Coordinator_Event_Recorder_Ignore_Events_In_List** is set to 0, only events listed in **Report_Coordinator_Event_Recorder_Events** appear. |


## Example


The following is an example of a ReportCoordinatorEventRecorder.csv report from a malaria simulation
using vector surveillance:

| Time | Coordinator_Name | Event_Name |
| --- | --- | --- |
| 200 | VectorSurveillance_Coordinator | StartVectorSurveillance |
| 200 | VectorSurveillance_Coordinator | VectorSurveyDone |
| 210 | VectorSurveillance_Coordinator | VectorSurveyDone |
| 220 | VectorSurveillance_Coordinator | VectorSurveyDone |
