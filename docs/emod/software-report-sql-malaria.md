# SqlReportMalaria


The SqlReportMalaria report extends [software-report-sql](software-report-sql.md) with malaria-specific health and
infection data. It is only available when **Simulation_Type** is MALARIA_SIM. The output is a
multi-table SQLite relational database (see [DB Browser for SQLite](https://sqlitebrowser.org/)
for more information). Use the configuration parameters to manage the size of the database.

`SqlReportMalariaGenetics` extends this report with parasite genetics data for FPG simulations.
See [software-report-sql-malaria-genetics](software-report-sql-malaria-genetics.md).


## Configuration


To generate this report, configure the following parameters in the custom_reports.json file:

```
Include_Health_Table, boolean, NA, NA, 1, "A true value (1) includes the Health table which has data for each time step for the health of an individual."
Include_Infection_Data_Table, boolean, NA, NA, 1, "A true value (1) includes the InfectionData table which has data for each time step for each active infection."
Include_Individual_Properties, boolean, NA, NA, 0, "Include a table with all the possible IPs and include the IP data for each person in the Health table."
Include_Drug_Status_Table, boolean, NA, NA, 0, "A true value (1) includes the table that provides data at each time step for each drug the person has."
Start_Day, float, 0, 3.40E+38, 0, "The day to start collecting data."
End_Day, float, 0, 3.40E+38, 3.40E+38, "The day to stop collecting data."
```

[link](../json/software-report-sql-malaria.json)

## SQL database and table structures


The report produces all tables from [software-report-sql](software-report-sql.md). The Health and InfectionData
tables are extended with malaria-specific columns, and two new tables are added.


## Humans table


The Humans table records all individuals in the simulation. It contains one row per individual
and has a one-to-many relationship with the Infections and Health tables.

```
RunNumber, integer, The seed to the random number generator from the **Run_Number** parameter.
HumanID, integer, The unique ID of the individual in the simulation.
Gender, text, "The gender of the individual. Possible values are M or F."
HomeNodeID, integer, "The external ID (NodeID in demographics) of the individual's home node."
InitialAgeDays, float, "The age of the individual in days when they entered the simulation."
SimTimeAdded, float, "The simulation time when the individual was added."
```

## Health table


The Health table records the health state of each individual at each time step. There is one row
per individual per time step. This table has a many-to-one relationship with the Humans table.
Omitted when **Include_Health_Table** is false. Query the SevereCaseType table to translate
SevereCaseTypeID values to text names.

```
RunNumber, integer, The seed to the random number generator from the **Run_Number** parameter.
HumanID, integer, The unique ID of the individual in the simulation.
NodeID, integer, The external ID of the node the individual is in at this time step.
SimTime, float, The simulation time when this data was collected.
Infectiousness, float, The individual's infectiousness to vectors at this time step.
RelativeBitingRate, float, "The relative rate at which this individual is bitten by mosquitoes, based on age and other factors."
IsClinicalCase, boolean, "1 if the individual has a fever exceeding both **Clinical_Fever_Threshold_Low** and **Clinical_Fever_Threshold_High**."
IsSevereCase, boolean, "1 if the individual has a fever exceeding **Clinical_Fever_Threshold_Low** and was probabilistically determined to have severe disease."
SevereCaseTypeID, integer, "The unique ID of the severe case type. Query the SevereCaseType table for the text name."
InvMicrolitersBlood, float, The inverse of the individual's blood volume in microliters.
RedBloodCellCount, float, The number of red blood cells the individual has.
Cytokines, float, The cytokine level stimulated by the presence of malaria parasites.
HRP2, float, "The amount of Histidine Rich Protein 2 (HRP2) in the individual's blood per microliter. Used to compare against HRP2 detection thresholds."
PfEMP1VariantFraction, float, "The fraction of PfEMP1 variants for which the individual has antibodies, out of **Falciparum_PfEMP1_Variants** total."
```

## SevereCaseType table


A small lookup table that maps SevereCaseTypeID values in the Health table to text names.

```
SevereCaseTypeID, integer, The unique ID of the severe case type.
Name, enum, "The name of the severe case type. Possible values are NONE, ANEMIA, PARASITES, or FEVER."
```

## Infections table


The Infections table records each infection that occurs in the simulation. There is one row per
infection. This table has a many-to-one relationship with the Humans table.

```
RunNumber, integer, The seed to the random number generator from the **Run_Number** parameter.
InfectionID, integer, The unique ID of the infection in the simulation.
HumanID, integer, The unique ID of the individual who acquired the infection.
SimTimeCreated, float, The simulation time when the infection was created.
```

## InfectionData table


The InfectionData table records data for each active infection at each time step. There is one
row per infection per time step. This table has a many-to-one relationship with the Infections
table. Omitted when **Include_Infection_Data_Table** is false.

```
RunNumber, integer, The seed to the random number generator from the **Run_Number** parameter.
InfectionID, integer, The unique ID of the infection in the simulation.
SimTime, float, The simulation time when this data was collected.
InfectedRedBloodCells, integer, The number of infected red blood cells due to this infection at this time step.
NumMatureGametocytesFemale, integer, The number of mature female gametocytes in this infection at this time step.
NumMatureGametocytesMale, integer, The number of mature male gametocytes in this infection at this time step.
```

## DrugStatus table


The DrugStatus table records the status of each active drug for each individual at each time step.
There may be multiple rows per individual per time step — one per active drug. Only present when
**Include_Drug_Status_Table** is true.

```
RunNumber, integer, The seed to the random number generator from the **Run_Number** parameter.
HumanID, integer, The unique ID of the individual in the simulation.
SimTime, float, The simulation time when this data was collected.
DrugName, string, "The name of the drug as defined by **Malaria_Drug_Params**."
CurrentEfficacy, float, The current efficacy of the drug.
NumRemainingDoses, integer, The number of doses the individual has yet to take.
```

## IndividualProperties table


A lookup table mapping individual property key-value IDs to their text names. Only present when
**Include_Individual_Properties** is true.

```
RunNumber, integer, The seed to the random number generator from the **Run_Number** parameter.
KeyValueID, integer, The unique ID of the IP key-value pair.
Key, text, The name of the individual property key.
Value, text, The value of the individual property.
```
