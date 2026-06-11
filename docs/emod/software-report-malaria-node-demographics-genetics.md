# ReportNodeDemographicsMalariaGenetics


The malaria genetics node demographics report (ReportNodeDemographicsMalariaGenetics.csv) extends
the data collected in the malaria node demographics report by adding data about the number of
infections with specific genetic barcodes. This report requires **Malaria_Model** to be set to
MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

!!! seealso
    [FPG model](malaria-model-fpg.md) — For an overview of the FPG model, genome configuration, and the full FPG workflow.

!!! note
    If you need detailed data on the infections with different barcodes, use the
    [SqlReportMalariaGenetics](software-report-sql-malaria-genetics.md). That report contains data on all barcodes, without specifying what they are.

## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

{{ read_csv('../csv/report-malaria-node-demographics-genetics.csv', keep_default_na=False) }}

```json
{
    "Reports": [
        {
            "Class": "ReportNodeDemographicsMalariaGenetics",
            "Age_Bins": [10, 100],
            "Barcodes": ["TA", "AT", "TT"],
            "Drug_Resistant_Stat_Type": "NUM_INFECTIONS",
            "Drug_Resistant_Strings": ["TA", "AT", "TT"],
            "IP_Key_To_Collect": "",
            "Stratify_By_Gender": 0,
            "Stratify_By_Has_Clinical_Symptoms": 0
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data


The report will contain the following output data, divided between stratification columns and data
columns.


### Stratification columns

| Parameter | Data type | Description |
| --- | --- | --- |
| `Time` | float | The day of the simulation that the data was collected. |
| `NodeID` | integer | The External ID of the node for the data in the row in the report. |
| `Gender` | enum | Possible values are M or F; the gender of the individuals in the row in the report. This column only appears if **Stratify_By_Gender** = 1. |
| `AgeYears` | float | The max age in years of the bin for the individuals in the row in the report. If **Age_Bins** is empty, this column does not appear. |
| `IndividualProp` | string | The value of the IP for the individuals in the row in the report. If **IP_Key_To_Collect** is an empty string, then this column does not appear. |
| `HasClinicalSymptoms` | enum | T implies that the people in the row are having clinical symptoms. F implies they do not. This column only appears if **Stratify_By_Has_Clinical_Symptoms** = 1. |

### Data columns

| Parameter | Data type | Description |
| --- | --- | --- |
| `NumIndividuals` | integer | The number of individuals who meet the stratification values. |
| `NumInfected` | integer | The number of infected individuals who meet the stratification values. |
| `NodeProp = <Node Property Keys>` | string | For each possible Node Property, there is one column where the data in the column is the value of that particular property. If there are no Node Properties, then there are no columns. |
| `AvgInfectiousness` | float | The average infectiousness to mosquitoes for the individuals of this row. Infectiousness is based on the number of mature gametocytes that the person has. |
| `AvgParasiteDensity` | float | The average true parasite density for the individuals of this row. |
| `AvgGametocyteDensity` | float | The average true gametocyte density for the individuals of this row. |
| `AvgVariantFractionPfEMP1Major` | float | For each individual, a count is made of the number of PfEMP1 Major antibodies the individual has and is divided by the total number of possible variants (Falciparum_PfEMP1_Variants). This is the average of this value for all the individuals represented in this row. |
| `AvgNumInfections` | float | The average number of infections for the people of this row. |
| `AvgInfectionClearedDuration` | float | The average duration to clear infections for the people of this row. |
| `NumInfectionsCleared` | integer | The number of cleared infections for the people of this row. |
| `NumHasFever` | integer | The number of people in the row that have a fever according to the diagnostic using the **Report_Detection_Threshold_Fever** parameter. |
| `NumHasClinicalSymptoms` | integer | If **Stratify_By_Has_Clinical_Symptoms** = 0, then this column is present with the number of people in the row that are considered to have 'clinical' symptoms. |
| `[barcodes]` | integer | The number of human infections with the barcode that is the column header. If you used a wild card at a loci, it includes all the barcodes that match the other loci exactly but ignores differences at this loci. For example, A*T includes AAT, ACT, AGT, and ATT. There will be one column for each barcode. |
| `OtherBarcodes` | integer | The number of human infections whose barcode is not counted by the other columns. |

## Example


The following is an example of a ReportNodeDemographicsMalariaGenetics.csv

{{ read_csv("csv/report-malaria-node-demographics-genetics.csv", keep_default_na=False) }}
