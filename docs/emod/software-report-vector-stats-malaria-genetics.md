# ReportVectorStatsMalariaGenetics


The vector statistics and malaria genetics report (ReportVectorStatsMalariaGenetics.csv) is a
CSV-formatted report similar to the [ReportVectorStats](software-report-vector-stats.md) report. It provides genetic
barcode information in addition to detailed life-cycle data on the vectors in the simulation. The
report is stratified by time, node ID, and (optionally) species.

When **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS, this report will
provide detailed insight into the status of the parasites in the vector population, including
details on the oocysts, sporozoites, biting, etc.

!!! seealso
    [Full parasite genetics](malaria-model-fpg.md) for more information on the FPG model.

## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

{{ read_csv('../csv/report-vector-stats-malaria-genetics.csv', keep_default_na=False) }}

```json
{
    "Reports": [
        {
            "class": "ReportVectorStatsMalariaGenetics",
            "Species_List": ["arabiensis", "funestus"],
            "Stratify_By_Species": 1,
            "Include_Wolbachia_Columns": 0,
            "Include_Gestation_Columns": 1,
            "Barcodes": ["AAAAAA", "AAAATTA"]
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data


The output report will contain the following information.

### Stratification columns


| Parameter | Data type | Description |
| --- | --- | --- |
| `Time` | integer | The day of the simulation that the data was collected. |
| `NodeID` | integer | The External ID of the node that the data is being collected for. |
| `Species` | string | If **Stratify_By_Species** = 1, then the species column will contain the name of the species for the given row. |

### Data columns


| Parameter | Data type | Description |
| --- | --- | --- |
| `Population` | integer | The number of people in the node. |
| `VectorPopulation` | integer | The number of adult female vectors that are in the STATE_INFECTIOUS, STATE_INFECTED, and STATE_ADULT. |
| `STATE_INFECTIOUS` | integer | The number of adult female vectors that are infectious. |
| `STATE_INFECTED` | integer | The number of adult female vectors that are infected. |
| `STATE_ADULT` | integer | The number of adult female vectors. |
| `STATE_MALE` | integer | The number of adult male vectors. |
| `STATE_IMMATURE` | integer | The number of immature vectors, includes male and female. |
| `STATE_LARVA` | integer | The number of larva, includes male and female. |
| `STATE_EGG` | integer | The number of eggs, includes male and female. |
| `NumLookingToFeed` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were looking to feed during this time step. |
| `NumFedCount` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that had a blood meal during this time step. |
| `NumGestatingBegin` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were gestating and did not die due to non-feeding mortality. |
| `NumGestatingEnd` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were gestating at the end of the time step. |
| `NumAttemptFeedIndoor` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that attempt to feed indoors. This group of vectors can still die indoors before they feed on a human. |
| `NumAttemptFeedOutdoor` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that attempt to feed outdoors. This group of vectors can still die outdoors before they feed on a human. |
| `NumAttemptButNotFeed` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were attempting to feed indoors or outdoors but did not die or feed on a human. They will look to feed during the next day. |
| `NewEggsCount` | integer | The number of eggs that were laid this day. |
| `IndoorBitesCount` | float | The number of bites made on humans indoors. This includes vectors that live for another day as well as those that die trying to get away. |
| `IndoorBitesCountInfectious` | float | The number of bites made by infectious vectors on humans indoors. This includes vectors that live for another day as well as those that die trying to get away. |
| `OutdoorBitesCount` | float | The number of bites made on humans outdoors. This includes vectors that live for another day as well as those that die trying to get away. |
| `OutdoorBitesCountInfectious` | float | The number of bites made by infectious vectors on humans outdoors. This includes vectors that live for another day as well as those that die trying to get away. |
| `UnmatedAdults` | float | The number of adult females that have not mated. This can be an important statistic when the male vector population is suppressed. When the male population is low, females moving from immature to adult might not find a male to mate with for several days. The female continues to feed but she does not produce fertile eggs. |
| `NewAdults` | integer | The number of female vectors that matured to adulthood this day. |
| `DiedBeforeFeeding` | integer | The number of vectors that died this time step due to local mortality, sugar feeding, outdoor area killing, etc. |
| `DiedDuringFeedingIndoor` | integer | The number of vectors that died indoors while attempting to feed (e.g. due to bed nets). |
| `DiedDuringFeedingOutdoor` | integer | The number of vectors that died outdoors while attempting to feed. |
| `NumDiedInfectious` | integer | If **Include_Death_By_State_Columns** = 1, then this column contains the number of infectious, mature, female vectors that died during this time step. |
| `NumDiedInfected` | integer | If **Include_Death_By_State_Columns** = 1, then this column contains the number of infected, mature, female vectors that died during this time step. |
| `NumDiedAdults` | integer | If **Include_Death_By_State_Columns** = 1, then this column contains the number of mature female vectors that are neither infected or infectious that died during this time step. |
| `NumDiedMale` | integer | If **Include_Death_By_State_Columns** = 1, then this column contains the number of mature male vectors that died during this time step. |
| `AvgAgeAtDeathInfectious` | float | If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the infectious, mature, female vectors that died during this time step. |
| `AvgAgeAtDeathInfected` | float | If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the infected, mature, female vectors that died during this time step. |
| `AvgAgeAtDeathAdults` | float | If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the mature, female vectors that are neither infected or infectious that died during this time step. |
| `AvgAgeAtDeathMale` | float | If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the mature male vectors that died during this time step. |
| `NumGestatingOnDay_0` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 0 more days before attempting to feed. |
| `NumGestatingOnDay_1` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 1 more days before attempting to feed. |
| `NumGestatingOnDay_2` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 2 more days before attempting to feed. |
| `NumGestatingOnDay_3` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 3 more days before attempting to feed. |
| `NumGestatingOnDay_4` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 4 more days before attempting to feed. |
| `NumGestatingOnDay_5` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 5 more days before attempting to feed. |
| `NumGestatingOnDay_6` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 6 more days before attempting to feed. |
| `NumGestatingOnDay_7` | integer | If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 7 more days before attempting to feed. |
| `VECTOR_WOLBACHIA_FREE` | integer | If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that are Wolbachia free. |
| `VECTOR_WOLBACHIA_A` | integer | If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that have Wolbachia A. |
| `VECTOR_WOLBACHIA_B` | integer | If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that have Wolbachia B. |
| `VECTOR_WOLBACHIA_AB` | integer | If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that have Wolbachia AB. |
| `MigrationFromCountLocal` | integer | The number of adult female vectors that made a local migration trip away from this node. |
| `MigrationFromCountRegional` | integer | The number of adult female vectors that made a regional migration trip away from this node. |
| `XXX_AvailableHabitat` | integer | If **Stratify_By_Species** = 0, then this column title does not have the species name in it. If **Stratify_By_Species** = 1, then there is a column for each species. This column contains the number of larva that the habitat could add (e.g. number of spots open); equal to current capacity - current larval count. |
| `XXX_EggCrowdingCorrection` | float | If **Stratify_By_Species** = 0, then this column title does not have the species name in it. If **Stratify_By_Species** = 1, then there is a column for each species. This column contains the probability that eggs die due to overcrowding. |
| `NumVectorsNone` | integer | The number of uninfected/noninfectious vectors; they contain neither oocysts nor sporozoites. |
| `NumVectorsOnlyOocysts` | integer | The number of vectors that are infected and contain only oocysts. The lack of sporozoites implies that the vectors are infected but not infectious. This is the stage before the oocysts turn into sporozoites. |
| `NumVectorsOnlySporozoites` | integer | The number of vectors that are infected and contain only sporozoites. The fact that the vectors have sporozoites means that they are infectious and give the sporozoites to humans. |
| `NumVectorsBothOocystsSporozoites` | integer | The number of vectors that have both oocysts and sporozoites. A vector can have both due to getting infected at different times by different bites. |
| `NumBitesAdults` | integer | The number of bites on humans made by uninfected vectors, neither infected or infectious. The vector that did the biting could have lived, died during feed, or died after feed. |
| `NumBitesInfected` | integer | The number of bites on humans made by a vector that is infected but not infectious. That is, a vector that only has oocysts. |
| `NumBitesInfectious` | integer | The number of bites on humans made by an infectious vector, e.g. has sporozoites. The vector could have both oocysts and sporozoites. This biting vector could die during feeding, after feeding, or live to the next day. |
| `NumDiedAdults` | integer | The number of uninfected vectors that died this day. They could have died from interventions, while trying to feed, or just old age. |
| `NumDiedInfected` | integer | The number of infected vectors that died this day. These vectors had oocysts but no sporozoites. |
| `NumDiedInfectious` | integer | The number of infectious vectors that died this day. These vectors must have had sporozoites, but they could have had oocysts as well. |
| `NumParasiteCohortsOocysts` | integer | The number of parasite cohorts in the oocyst state counted from all of the infected vectors. Each cohort is unique based on the vector it is in, the age, and the parasite genome. |
| `NumParasiteCohortsSporozoites` | integer | The number of parasite cohorts in the sporozoite state counted from all of the vectors that contain them. Each cohort is unique based on the vector it is in, the age, and the parasite genome. |
| `NumOocysts` | integer | The number of oocysts in the vector population. |
| `NumSporozoites` | integer | The number of sporozoites in the vector population. |
| `NumInfectiousToAdult` | integer | The number of vectors that transitioned from infectious (had sporozoites) to adult (having no sporozoites or oocysts). |
| `NumInfectiousToInfected` | integer | The number of vectors that transitioned from infectious (had sporozoites) to infected (having only oocysts). |
| `\<Barcode\>` | integer | Number of vectors with sporozoites with the indicated barcode. If a wild card ('*') is used, then it is the number of vectors in that group that contain sporozoites. The barcode indicated is provided by the user in the **Barcodes** parameter. |
| `OtherBarcodes` | integer | The number of vectors with sporozoites having a barcode different from those specified by the user. This column only appears when the user specifies barcodes in the **Barcodes** parameter. |

## Example


The following is an example of a ReportVectorStatsMalariaGenetics.csv file.


{{ read_csv("csv/report-vector-stats-malaria-genetics.csv", keep_default_na=False) }}
