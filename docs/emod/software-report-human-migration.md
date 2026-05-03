# ReportHumanMigrationTracking


The human migration tracking report (ReportHumanMigrationTracking.csv) is a CSV-formatted report
that provides details about human travel during simulations. The finished report will provide one
line for each surviving individual that migrates during the simulation.


## Configuration


There are no special parameters that need to be configured to generate the report. However, the
simulation must have migration enabled (see the migration parameters in [parameter-configuration](parameter-configuration.md)).


## Report structure and channel descriptions


The file contains the following data channels:

```
Time, integer, The day that an individual leaves their current node.
IndividualID, integer, The ID of the migrating individual.
AgeYears, integer, The age (in years) of the migrating individual.
Gender, string, "The gender of the individual. Possible values are M or F."
IsAdult, enum, "Possible values are T or F; T (true) if individual's age is greater than the configuration parameter **Minimum_Adult_Age_Years.**"
Home_NodeID, string, The external ID of the node the individual considers to be their 'home' node.
From_NodeID, string, The external ID of the node the individual is moving from.
To_NodeID, string, the external ID of the node the individual is moving to.
MigrationType, enum, "The type of migration that is occurring. When the event is SimulationEnd, the values are either 'home' or 'away,' indicating if the individual was in their home node or not when the simulation ended. Otherwise, possible values are air, local, sea, regional, local, family, or intervention."
Event, enum, "Possible values are Emigrating, NonDiseaseDeaths, DiseaseDeaths, or SimulationEnd. Emigrating means the individual is moving, SimulationEnd means the simulation has finished."
```

## Example


The following is an example of ReportHumanMigrationTracking.csv.

{{ read_csv("reporthumanmigration.csv") }}
