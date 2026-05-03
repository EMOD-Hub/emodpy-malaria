# ReportFpgOutputForObservationalModel


FPG simulations have complete knowledge of every parasite genome in the population, but real-world
genomic surveillance collects data through specific sampling strategies that capture only a fraction
of infections. `ReportFpgOutputForObservationalModel` bridges this gap by extracting the complete
genetic data on all filtered infected individuals, allowing post-processing tools such as the
[FPGObservationalModel](https://github.com/EMOD-Hub/FPGObservationalModel) to apply realistic
surveillance sampling strategies and study what genetic signals different approaches can detect.

Unlike most EMOD reports, which produce a single output file named after the report class, this
report produces a three-file ensemble: **infIndexRecursive-genomes-df.csv**, **variants.npy**, and
**roots.npy**. This report is intended for simulations where **Malaria_Model** is set to
MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

## Output files


* **infIndexRecursive-genomes-df.csv** - A list of infected individuals in each node at each time
  step, where each row represents one person.
* **variants.npy** - A numpy binary file containing the nucleotide sequence data for each genome
  referenced in the **recursive_nid** column of infIndexRecursive-genomes-df.csv. The row index
  into this array corresponds to the genome index values in **recursive_nid**.
* **roots.npy** - A numpy binary file containing the allele root data for each genome referenced
  in the **recursive_nid** column of infIndexRecursive-genomes-df.csv. The row index into this
  array corresponds to the genome index values in **recursive_nid**.

### Configuration


To generate this report, configure the following parameters in the custom_reports.json file:

```
Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
End_Day,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data. If you want data collected on a specific day, enter that day plus 1."
Node_IDs_Of_Interest,"array of integers","1","2.14748e+09","[]","Data will be collected for the nodes in this list. Empty list implies all nodes."
Min_Age_Years,"float","0","125","0","Minimum age in years of people to include in the report."
Max_Age_Years,"float","0","125","125","Maximum age in years of people to include in the report."
Must_Have_IP_Key_Value,"string","NA","NA","(empty string)","A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
Must_Have_Intervention,"string","NA","NA","(empty string)","The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
Minimum_Parasite_Density,"float","0","3.40282e+38","1.0","The minimum parasite density (asexual parasites per microliter of blood) that an infection must have to be included. A non-zero value filters out hepatocyte-stage infections and those with only gametocytes."
Sampling_Period,"float","1","3.40282e+38","1","The number of days between sampling the population. Data is collected on days Start_Day, Start_Day + Sampling_Period, Start_Day + 2*Sampling_Period, and so on."
Include_Genome_IDs,"boolean","NA","NA","0","If true (1), an additional genome_ids column is appended to the CSV output containing EMOD's internal ID for the genome of each infection's parasite. This ID can be used to cross-reference genome data with other EMOD reports that include genome IDs."
```

[link](../json/software-report-fpg-output-observational-model.json)

This example collects data after running for 10 years and collects it for the next 2 years. It only
collects data from nodes 1 and 3 for children 5 and under who have accessibility to healthcare and are
taking anti-malarial drugs. The infections must have a parasite density of at least 1.0.
The Sampling_Period of 30.4166667 is 365/12, resulting in 12 collections per year (approximately
monthly). The report will have entries for the following days:

3650, 3681, 3711, 3742, 3772, 3803, 3833, 3863, 3894, 3924, 3955, 3985,
4015, 4046, 4076, 4107, 4137, 4168, 4198, 4228, 4259, 4289, 4320, 4350,
4380

There are 25 entries — the initial collection on day 3650 plus 24 subsequent monthly collections,
ending on day 4380 (exactly two years later). End_Day is set to 4381 rather than 4380 because the
report collects data only on days strictly less than End_Day; it must be set one day past the last
desired collection day to include it.


### Output file: infIndexRecursive-genomes-df.csv


Each row of the report represents one infected person sampled at a given time step. Only individuals
with at least one infection meeting the **Minimum_Parasite_Density** threshold are included.
The report contains the following columns:

```
population, integer, The external ID of the node the person is currently in.
year, integer, "The year of the data starting at zero. Used as a label for the time bin of data."
month, integer, "A value from 0 to 11 that, together with the year column, specifies the time bin of data."
infIndex, integer, A unique identifier for this row of data; an increasing integer with each row.
day, float, "The day of the simulation in EMOD. The year and month values correspond to this day. For example, if day is 715, then year=1 and month=11."
count, (not used), This column is not used.
age_day, float, The age of the person in days.
fever_status, integer, "0 = no fever, 1 = has fever (clinical disease symptoms present)."
recursive_nid, array of integers, "A quoted list of genome indices — one per qualifying infection the person has — where each value is the row index into variants.npy and roots.npy for that infection's genome data (e.g., ""[0,1,2]""). The entries in recursive_nid, infection_ids, bite_ids, and genome_ids are parallel arrays: the i-th entry in each refers to the same infection."
recursive_count, integer, "The number of active infections meeting the Minimum_Parasite_Density threshold; equals the number of entries in recursive_nid."
IndividualID, integer, The unique ID of the person in EMOD.
infection_ids, array of integers, "A quoted list of unique EMOD infection IDs, one per qualifying infection. Entries are in the same order as recursive_nid."
bite_ids, array of integers, "A quoted list of bite IDs, one per qualifying infection, identifying the mosquito bite that initiated each infection. Entries are in the same order as recursive_nid."
genome_ids, array of integers, "(Optional) A quoted list of EMOD's internal genome IDs, one per qualifying infection. Entries are in the same order as recursive_nid. Only present when Include_Genome_IDs is set to true (1)."
```

### Example


The following is an example of infIndexRecursive-genomes-df.csv:

```none
population,year,month,infIndex,day,count,age_day,fever_status,recursive_nid,recursive_count,IndividualID,infection_ids,bite_ids,genome_ids
1,0,9,0,300,,1108.94,1,"[0,1,2,3,4,5,6,7,8,9]",10,2,"[2534,3364,3643,7816,7817,7818,7819,10932,10933,10934]","[497532,526283,537262,613210,613210,613210,613210,661772,661772,661772]","[14,4,10,7714,7717,7718,34,22,525,15318]"
1,0,9,1,300,,8153.8,1,"[10,11,12,13,14,15,16,17,1]",9,3,"[2428,6284,6285,6286,9469,9470,10935,10936,10937]","[495486,592462,592462,592462,636574,636574,662177,662177,662177]","[40,4933,4935,20,734,38,25625,25630,4]"
1,0,9,2,300,,843.391,1,"[18,19,20,21,22,23]",6,4,"[2348,7820,8390,8391,8392,8393]","[491221,612500,619455,619455,619455,619455]","[36,8,9474,32,9478,9479]"
1,0,9,3,300,,1729.52,1,"[19,24,25,26,27,6,28,0,29,30]",10,5,"[2260,7609,8018,8019,8394,8395,8396,8397,8972,8973]","[490394,611028,615591,615591,620939,620939,620939,620939,628136,628136]","[8,12,8320,8321,7715,34,12260,14,14459,14460]"
1,0,9,4,300,,6368.14,1,"[1,18,0,0,31,0,2,32,33,10]",10,6,"[2811,2812,4743,4892,5869,5870,6473,7249,7821,10522]","[504919,504919,569421,572401,586119,586119,595298,604633,611201,652666]","[4,36,14,14,3778,14,10,5748,9325,40]"
```
