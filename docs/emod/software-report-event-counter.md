# ReportEventCounter


The event counter report (ReportEventCounter.json) is a JSON-formatted file that keeps track of how
many of each event types occurs during a time step. The report produced is similar to the
InsetChart.json channel report, where there is one channel for each event defined in the
configuration file (config.json). This report only counts events; a similar report,
[ReportEventRecorder](software-report-event-recorder.md), will provide information about the person at the time of the
event.



## Configuration


The following parameters need to be configured to generate the report:

{{ read_csv('../csv/report-event-counter.csv', keep_default_na=False) }}

```json
{
    "Reports": [{
        "class": "ReportEventCounter",
        "Filename_Suffix": "Node1",
        "Start_Day": 365,
        "End_Day": 465,
        "Node_IDs_Of_Interest": [ 1 ],
        "Min_Age_Years": 5,
        "Max_Age_Years": 10,
        "Must_Have_IP_Key_Value": "Risk:HIGH",
        "Must_Have_Intervention": "SimpleVaccine",
        "Event_Trigger_List": ["NewInfectionEvent", "NewClinicalCase"]
    }],
    "Use_Defaults": 1
}
```

## Header


The header section contains the following parameters:

| Parameter | Data type | Description |
| --- | --- | --- |
| `Channels` | integer | The number of entries in the 'Channels' map (e.g. the number of events that the report is counting). |
| `DTK_Version` | string | The version of EMOD that was used. |
| `DateTime` | string | The date and time the report was created. |
| `Report_Type` | string | The type of report created (it should always be InsetChart/Channel Report). |
| `Report_Version` | string | The version of the report format. |
| `Simulation_Timestep` | integer | The number of days in one time step of the simulation. |
| `Timesteps` | integer | The number of time steps recorded in the file. Each channel should have this number of entries. |

## Channels


The channels section contains the following parameters:

| Parameter | Data type | Description |
| --- | --- | --- |
| `<Event Names>` | string | The name of the event. |
| `Data` | array | An array of event counts where each entry is the number of events that occurred during the timestep. |
| `Units` | string | Empty string, but it is the 'event count'. |

## Example


The following is an example of ReportEventCounter.json.

```json
{
    "Header": {
        "Channels": 4,
        "DTK_Version": "4148 Malaria-Ongoing (bb265ad) May 16 2019 09:39:35",
        "DateTime": "Tue Mar 12 15:16:08 2019",
        "Report_Type": "InsetChart",
        "Report_Version": "3.2",
        "Simulation_Timestep": 1,
        "Start_Time": 0,
        "Timesteps": 3
    },
    "Channels": {
        "Births": {"Data": [0, 1, 1], "Units": ""},
        "EveryUpdate": {"Data": [1000, 1001, 1002], "Units": ""},
        "NewInfectionEvent": {"Data": [110, 0, 2], "Units": ""},
        "NonDiseaseDeaths": {"Data": [0, 0, 0], "Units": ""}
    }
}
```
