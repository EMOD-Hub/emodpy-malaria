# ReportVectorGenetics


The vector genetics report is a CSV-formatted report that collects information on how many vectors
of each genome/allele combination exist at each time, node, and vector state. Information can only
be collected on one species per report.




## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json file:

```
Filename_Suffix, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
End_Day,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
Node_IDs_Of_Interest,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list.  Empty list implies all nodes."
Allele_Combinations_For_Stratification, array of strings, NA, NA, [], "If stratifying by allele, this will be the list of alleles to stratify by. Depends on **Stratify_By** = ALLELE."
Alleles_For_Stratification, array of strings, NA, NA, [], "The list of alleles for which to collect frequency counts. If the list is empty, the report uses a list of all possible alleles. Depends on **Stratify_By** = ALLELE_FREQ"
Combine_Similar_Genomes, boolean, NA, NA, [], "If set to true (1), genomes are combined for each locus (ignoring gender) if the set of alleles of the two genomes are the same. Note that '1-0' is considered to be the same as '0-1'. Depends on **Stratify_By** = GENOME or SPECIFIC_GENOME."
Gender, enum, NA, NA, VECTOR_FEMALE, "The gender to include in the file; possible values are VECTOR_FEMALE, VECTOR_MALE, and VECTOR_BOTH_GENDERS."
Include_Vector_State_Columns, boolean, NA, NA, 1, "If set to true (1), the columns for each vector state (Eggs, Larvae, etc) will be included."
Include_Death_By_State_Columns, boolean, NA, NA, 0, "Adds columns for the number of vectors that died in this state during this time step as well as the average age at death.  It adds two columns for each of the following states: ADULT, INFECTED, INFECTIOUS, and MALE."
Species, string, NA, NA, "(if not specified, the first species found will be used)", "The species to include information on; the name must exist in **Vector_Species_Params** in the config.json file. The name will be added to the report name."
Specific_Genome_Combinations_For_Stratification, array of strings, NA, NA, NA, "If stratifying by SPECIFIC_GENOME, this is the list of genomes to stratify by. '*' will list all entries at that location, and '?' will combine all entries at that location. Depends on **Stratify_By** = SPECIFIC_GENOME."
Stratify_By, enum, NA, NA, GENOME, "Determines how the report will be stratified; possible values are GENOME, SPECIFIC_GENOME, and ALLELE."
```

The following is an example of an input file for this report:

[link](../json/software-report-vector-genetics.json)

## Output file data


The output report will contain the following information.

### Stratification columns


```
Time, integer, "The day of the simulation that the data was collected."
NodeID, integer, "The External ID of the node that the data is being collected for."
Alleles, string, "If **Stratify_By** = ALLELE, then the column will be all of the possible alleles plus the values in **Allele_Combinations_For_Stratification**."
Genome, string, "If **Stratify_By** = GENOME or SPECIFIC_GENOME, then this is the 'Genome' column and for each time and NodeID, the column will contain the possible combinations of genomes."
```

### Data columns


```
VectorPopulation, integer, "If **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the number of female vectors that are in the states STATE_INFECTIOUS, STATE_INFECTED, or STATE_ADULT."
STATE_INFECTIOUS, integer, "If **Gender** is VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the number of female vectors that are in this state."
STATE_INFECTED, integer, "If **Gender** is VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the number of female vectors that are in this state."
STATE_ADULT, integer, "If **Gender** is VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the number of female vectors that are in this state."
STATE_MALE, integer, "If **Gender** is VECTOR_BOTH_GENDERS or VECTOR_MALE, then this column will contain the number of mature male vectors."
STATE_IMMATURE, integer, "This column  contains the number of vectors (male and female) in the 'immature' state."
STATE_LARVA, integer, "This column  contains the number of larva (male and female)."
STATE_EGG, integer, "This column contains the number of eggs (male and female)."
VectorPopulationNumDied, integer, "If **Include_Death_By_State_Columns** is true and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the number of female vectors that died and were in states STATE_INFECTIOUS, STATE_INFECTED, or STATE_ADULT."
InfectiousNumDied, integer, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the  number of infectious, mature, female vectors that died during this time step."
InfectedNumDied, integer, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the number of infected, mature, female vectors that died during this time step."
AdultsNumDied, integer, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the number of mature female vectors that are neither infected or infectious that died during this time step."
MaleNumDied, integer, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_MALE, then this column will contain the number of mature male vectors that died during this time step."
VectorPopulationAvgAgeAtDeath, float, "If **Include_Death_By_State_Columns** is true and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the average age (in days) of the the infectious, mature, female vectors that died during this time step."
InfectiousAvgAgeAtDeath, float, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the average age (in days) of the the infectious, mature, female vectors that died during this time step."
InfectedAvgAgeAtDeath, float, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the average age (in days) of the the infected, mature, female vectors that died during this time step."
AdultsAvgAgeAtDeath, float, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_FEMALE, then this column will contain the average age (in days) of the the mature, female vectors that are neither infected or infectious that died during this time step."
MaleAvgAgeAtDeath, float, "If **Include_Death_By_State_Columns** is true, **Include_Vector_State_Columns** is true, and **Gender** = VECTOR_BOTH_GENDERS or VECTOR_MALE, then this column will contain the average age (in days) of the the mature male vectors that died during this time step."
```

## Example


The following are examples of ReportVectorGenetics.csv files.  The Death By State columns are not included in the examples.

This table is stratified by genome and female vectors.

{{ read_csv("../csv/ReportVectorGenetics-genome-female.csv") }}

This table is stratified by genome and male vectors.

{{ read_csv("../csv/ReportVectorGenetics-genome-male.csv") }}

This table is stratified by allele and female vectors, with vector state columns included.

{{ read_csv("../csv/ReportVectorGenetics-allele-female.csv") }}
