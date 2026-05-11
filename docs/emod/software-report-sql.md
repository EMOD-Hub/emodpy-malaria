# SqlReport


The SqlReport report outputs individual-level epidemiological data for any EMOD simulation type.
Because of the quantity and complexity of the data, the report output is a multi-table SQLite
relational database (see [DB Browser for SQLite][sqlite-browser] for more
information). Use the configuration parameters to manage the size of the database.

`SqlReportMalaria` extends this report with malaria-specific health and infection data. See
[ReportSQLMalaria](software-report-sql-malaria.md).


## Configuration


To generate this report, configure the following parameters in the custom_reports.json file:

{{ read_csv('../csv/report-sql.csv', keep_default_na=False) }}

```json
{
    "Reports": [
        {
            "class": "SqlReport",
            "Include_Health_Table": 1,
            "Include_Infection_Data_Table": 1,
            "Start_Day": 100,
            "End_Day": 900
        }
    ],
    "Use_Defaults": 1
}
```

## SQL database and table structures


Because the output is a relational database, most tables have a primary key that is a combination
of RunNumber and another value. Because RunNumber is part of the primary key, data from multiple
simulation runs can be combined in a single database.


## Humans table


The Humans table records all individuals in the simulation. It contains one row per individual
and has a one-to-many relationship with the Infections and Health tables.

| Parameter | Data type | Description |
| --- | --- | --- |
| `RunNumber` | integer | The seed to the random number generator from the **Run_Number** parameter. |
| `HumanID` | integer | The unique ID of the individual in the simulation. |
| `Gender` | text | The gender of the individual. Possible values are M or F. |
| `HomeNodeID` | integer | The external ID (NodeID in demographics) of the individual's home node. |
| `InitialAgeDays` | float | The age of the individual in days when they entered the simulation. |
| `SimTimeAdded` | float | The simulation time when the individual was added. |

## Health table


The Health table records the health state of each individual at each time step. There is one row
per individual per time step. This table has a many-to-one relationship with the Humans table.
Omitted when **Include_Health_Table** is false. When **Include_Individual_Properties** is true,
one additional column is added for each individual property key, containing the ID of the
individual's current value for that IP (cross-referenced via the IndividualProperties table).

| Parameter | Data type | Description |
| --- | --- | --- |
| `RunNumber` | integer | The seed to the random number generator from the **Run_Number** parameter. |
| `HumanID` | integer | The unique ID of the individual in the simulation. |
| `NodeID` | integer | The external ID of the node the individual is in at this time step. |
| `SimTime` | float | The simulation time when this data was collected. |
| `Infectiousness` | float | The individual's infectiousness to vectors at this time step. |

## Infections table


The Infections table records each infection that occurs in the simulation. There is one row per
infection. This table has a many-to-one relationship with the Humans table.

| Parameter | Data type | Description |
| --- | --- | --- |
| `RunNumber` | integer | The seed to the random number generator from the **Run_Number** parameter. |
| `InfectionID` | integer | The unique ID of the infection in the simulation. |
| `HumanID` | integer | The unique ID of the individual who acquired the infection. |
| `SimTimeCreated` | float | The simulation time when the infection was created. |

## InfectionData table


The InfectionData table records data for each active infection at each time step. There is one
row per infection per time step. This table has a many-to-one relationship with the Infections
table. Omitted when **Include_Infection_Data_Table** is false.

| Parameter | Data type | Description |
| --- | --- | --- |
| `RunNumber` | integer | The seed to the random number generator from the **Run_Number** parameter. |
| `InfectionID` | integer | The unique ID of the infection in the simulation. |
| `SimTime` | float | The simulation time when this data was collected. |

## IndividualProperties table


A lookup table mapping individual property key-value IDs to their text names. Only present when
**Include_Individual_Properties** is true.

| Parameter | Data type | Description |
| --- | --- | --- |
| `RunNumber` | integer | The seed to the random number generator from the **Run_Number** parameter. |
| `KeyValueID` | integer | The unique ID of the IP key-value pair. |
| `Key` | text | The name of the individual property key. |
| `Value` | text | The value of the individual property. |
