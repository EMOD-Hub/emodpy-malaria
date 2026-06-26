# ReportNodeEventRecorder


The node event recorder report (ReportNodeEventRecorder.csv) provides information on the node's
population and health status at the time of a node-level event. Node-level events are broadcast by
interventions such as [BroadcastNodeEvent](parameter-campaign-node-broadcastnodeevent.md) and
node-level intervention distributions.

Additionally, it is possible to break down the population data by specific node properties and
individual properties, using the configuration parameters described below.

For recording individual-level events, see [ReportEventRecorder](software-report-event-recorder.md).
For coordinator-level events, see [ReportCoordinatorEventRecorder](software-report-coordinator-event-recorder.md).


## Configuration


To generate this report, the following parameters must be configured in the config.json file:

{{ read_csv('../csv/report-node-event-recorder.csv', keep_default_na=False) }}

```json
{
    "Report_Node_Event_Recorder": 1,
    "Report_Node_Event_Recorder_Events": ["SpaceSpraying", "Larvicides"],
    "Report_Node_Event_Recorder_Ignore_Events_In_List": 0,
    "Report_Node_Event_Recorder_Node_Properties": [],
    "Report_Node_Event_Recorder_Stats_By_IPs": []
}
```


## Output file data


The report (ReportNodeEventRecorder.csv) contains one row per node event. The columns are described
below.

### Base columns

These columns are always present.

| Data channel | Data type | Description |
| --- | --- | --- |
| `Time` | float | The simulation time (in days) when the node event occurred. |
| `NodeID` | integer | The identification number of the node where the event occurred. |
| `NodeEventName` | string | The name of the node event being logged. If **Report_Node_Event_Recorder_Ignore_Events_In_List** is set to 0, only events listed in **Report_Node_Event_Recorder_Events** appear. |
| `NumIndividuals` | integer | The total number of individuals in the node at the time of the event. |
| `NumInfected` | integer | The number of infected individuals in the node at the time of the event. |

### Node property columns

If **Report_Node_Event_Recorder_Node_Properties** is configured with one or more node property key
names, an additional column is added for each key listed. Each column shows the node's current value
for that property at the time of the event.

### Individual property (IP) breakdown columns

If **Report_Node_Event_Recorder_Stats_By_IPs** is configured with one or more individual property
(IP) key names, additional column pairs are appended for each key-value combination defined in the
demographics file. For example, if ``Risk`` has values ``HIGH`` and ``LOW``, the following columns
are added:

| Data channel | Data type | Description |
| --- | --- | --- |
| `Risk:HIGH:NumIndividuals` | integer | The number of individuals in the node whose ``Risk`` property is ``HIGH``. |
| `Risk:HIGH:NumInfected` | integer | The number of infected individuals in the node whose ``Risk`` property is ``HIGH``. |
| `Risk:LOW:NumIndividuals` | integer | The number of individuals in the node whose ``Risk`` property is ``LOW``. |
| `Risk:LOW:NumInfected` | integer | The number of infected individuals in the node whose ``Risk`` property is ``LOW``. |

The column naming convention is ``<Key>:<Value>:NumIndividuals`` and ``<Key>:<Value>:NumInfected``
for each IP key-value pair.


## Example


The following is an example of a ReportNodeEventRecorder.csv report from a malaria simulation
that uses node-level vector control interventions:

| Time | NodeID | NodeEventName | NumIndividuals | NumInfected |
| --- | --- | --- | --- | --- |
| 116 | 1 | SpaceSpraying | 993 | 852 |
| 121 | 1 | IndoorSpaceSpraying | 993 | 854 |
| 126 | 1 | MultiInsecticideSpaceSpraying | 990 | 847 |
| 131 | 1 | Larvicides | 988 | 843 |
| 136 | 1 | ScaleLarvalHabitat | 986 | 840 |
| 141 | 1 | OutdoorRestKill | 983 | 836 |
| 146 | 1 | SugarTrap | 980 | 832 |
| 151 | 1 | SpatialRepellent | 978 | 829 |
