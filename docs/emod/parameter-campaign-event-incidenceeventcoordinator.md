# IncidenceEventCoordinator


The **IncidenceEventCoordinator** coordinator class distributes interventions based on the number of events counted over a period of time.


{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-incidenceeventcoordinator.csv") }}

```json
{
    "class": "IncidenceEventCoordinator",
    "Number_Repetitions" : 3,
    "Timesteps_Between_Repetitions" : 6
}
```
