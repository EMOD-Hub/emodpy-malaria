# ReportMicrosporidia


The microsporidia report (ReportMicrosporidia.csv) tracks vector population counts broken down by
species and microsporidia strain at each time step. For every combination of species and strain —
including a "NoMicrosporidia" row representing uninfected vectors — it reports the number of
vectors in each life stage. This report is useful for monitoring how microsporidia spreads through
vector populations over time.

This report is available for `VECTOR_SIM` and `MALARIA_SIM` simulations.


## Configuration


To generate this report, add the following to the custom_reports.json file. This report has no
configurable parameters beyond the class name.

[link](../json/software-report-microsporidia.json)

## Output file data


The output file is named `ReportMicrosporidia.csv`. One row is written per time step, per node,
per species, and per microsporidia strain. A row with `MicrosporidiaStrain` = `NoMicrosporidia`
is included for each species and represents vectors not carrying any microsporidia strain.

```
Time, float, "The simulation time in days when the data was collected."
NodeID, integer, "The external ID of the node that the data is being collected for."
Species, string, "The name of the vector species."
MicrosporidiaStrain, string, "The name of the microsporidia strain. A value of ``NoMicrosporidia`` indicates vectors not infected with any strain."
VectorPopulation, integer, "The total number of adult female vectors in this species/strain group (STATE_INFECTIOUS + STATE_INFECTED + STATE_ADULT)."
STATE_INFECTIOUS, integer, "The number of adult female vectors that are infectious."
STATE_INFECTED, integer, "The number of adult female vectors that are infected but not yet infectious."
STATE_ADULT, integer, "The number of uninfected adult female vectors."
STATE_MALE, integer, "The number of adult male vectors."
STATE_IMMATURE, integer, "The number of immature vectors (male and female)."
STATE_LARVA, integer, "The number of larvae (male and female)."
STATE_EGG, integer, "The number of eggs (male and female)."
```

## Example


The following is an example of ReportMicrosporidia.csv.

{{ read_csv("csv/report-microsporidia.csv") }}
