=================
ReportVectorStats
=================

The vector statistics report (ReportVectorStats.csv) is a CSV-formatted report that provides
detailed life-cycle data on the vectors in the simulation. The report is stratified by time,
node ID, and (optionally) species.



Configuration
=============

To generate this report, the following parameters must be configured in the custom_reports.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Species_List, array of strings, NA, NA, [ ], "The species for which to include information. If the list is empty or absent, then data for all species will be collected."
    Stratify_By_Species, boolean, NA, NA, 0, "If set to true (1), then data will be stratified by species for each node."
    Include_Wolbachia_Columns, boolean, NA, NA, 0, "If set to true (1), columns will be added for each type of Wolbachia. Summation of columns should be equal to VectorPopulation."
    Include_Gestation_Columns, boolean, NA, NA, 0, "If set to true (1), columns will be added for feeding and gestation."
    Include_Death_By_State_Columns, boolean, NA, NA, 0, "Adds columns for the number of vectors that died in this state during this time step as well as the average age at death.  It adds two columns for each of the following states: ADULT, INFECTED, INFECTIOUS, and MALE."
    Include_Microsporidia_Columns, boolean, NA, NA, 0, "If set to true (1), columns will be added for each state and the value in the column will be the number of vectors that have microsporidia in that state during this time step."


.. code-block:: json

    {
        "Reports": [
            {
                "class": "ReportVectorStats",
                "Species_List":  [
                    "arabiensis",
                    "funestus"
                ],
                "Stratify_By_Species": 1,
                "Include_Wolbachia_Columns": 0,
                "Include_Gestation_Columns": 1,
                "Include_Microsporidia_Columns": 0,
                "Include_Death_By_State_Columns": 1
            }
        ],
        "Use_Defaults": 1
    }



Output file data
================

The output report will contain the following information.

Stratification columns
----------------------

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    Time, integer, "The day of the simulation that the data was collected."
    NodeID, integer, "The External ID of the node that the data is being collected for."
    Species, string, "If **Stratify_By_Species** = 1, then the species column will contain the name of the species for the given row."



Data columns
------------

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    Population, integer, "The number of people in the node."
    VectorPopulation, integer, "The number of adult female vectors that are in the STATE_INFECTIOUS, STATE_INFECTED, and STATE_ADULT."
    STATE_INFECTIOUS, integer, "The number of adult female vectors that are infectious."
    STATE_INFECTED, integer, "The number of adult female vectors that are infected."
    STATE_ADULT, integer, "The number of adult female vectors."
    STATE_MALE, integer, "The number of adult male vectors."
    STATE_IMMATURE, integer, "The number of immature vectors, includes male and female."
    STATE_LARVA, integer, "The number of larva, includes male and female."
    STATE_EGG, integer, "The number of eggs, includes male and female."
    NumLookingToFeed, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were looking to feed during this time step."
    NumFedCount, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that had a blood meal during this time step."
    NumGestatingBegin, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were gestating and did not die due to non-feeding mortality."
    NumGestatingEnd, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were gestating at the end of the time step."
    NumAttemptFeedIndoor, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that attempt to feed indoors.  This group of vectors can still die indoors before they feed on a human."
    NumAttemptFeedOutdoor, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that attempt to feed outdoors.  This group of vectors can still die outdoors before they feed on a human."
    NumAttemptButNotFeed, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of adult female vectors that were attempting to feed indoors or outdoors but did not die or feed on a human.  They will look to feed during the next day."
    NewEggsCount, integer, "The number of eggs that were laid this day."
    IndoorBitesCount, float, "The number of bites made on humans indoors.  This includes vectors that live for another day as well as those that die trying to get away."
    IndoorBitesCountInfectious, float, "The number of bites made by infectious vectors on humans indoors.  This includes vectors that live for another day as well as those that die trying to get away."
    OutdoorBitesCount, float, "The number of bites made on humans outdoors.  This includes vectors that live for another day as well as those that die trying to get away."
    OutdoorBitesCountInfectious, float, "The number of bites made by infectious vectors on humans outdoors.  This includes vectors that live for another day as well as those that die trying to get away."
    UnmatedAdults, float, "The number of adult females that have not mated.  This can be an important statistic when the male vector population is suppressed.  When the male population is low, females moving from immature to adult might not find a male to mate with for several days.  The female continues to feed but she does not produce fertile eggs."
    NewAdults, integer, "The number of female vectors that matured to adulthood this day."
    DiedBeforeFeeding, integer, "The number of vectors that died this time step due to local mortality, sugar feeding, outdoor area killing, etc."
    DiedDuringFeedingIndoor, integer, "This is the number of vectors that died indoors while attempting to feed (e.g. due to bed nets)."
    NumDiedInfectious, integer, "If **Include_Death_By_State_Columns** = 1, then this column contains the number of infectious, mature, female vectors that died during this time step."
    NumDiedInfected, integer, "If **Include_Death_By_State_Columns** = 1, then this column contains the number of infected, mature, female vectors that died during this time step."
    NumDiedAdults, integer, "If **Include_Death_By_State_Columns** = 1, then this column contains the number of mature female vectors that are neither infected or infectious that died during this time step."
    NumDiedMale, integer, "If **Include_Death_By_State_Columns** = 1, then this column contains the number of mature male vectors that died during this time step."
    AvgAgeAtDeathInfectious, float, "If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the the infectious, mature, female vectors that died during this time step."
    AvgAgeAtDeathInfected, float, "If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the the infected, mature, female vectors that died during this time step."
    AvgAgeAtDeathAdults, float, "If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the the mature, female vectors that are neither infected or infectious that died during this time step."
    AvgAgeAtDeathMale, float, "If **Include_Death_By_State_Columns** = 1, then this column contains the average age (in days) of the the mature male vectors that died during this time step."
    AvgDurationLarvaeToImmature, float, "Average time, in days, it takes larva to become immature adults."
    NumGestatingOnDay_0, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 0 more days before attempting to feed."
    NumGestatingOnDay_1, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 1 more days before attempting to feed."
    NumGestatingOnDay_2, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 2 more days before attempting to feed."
    NumGestatingOnDay_3, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 3 more days before attempting to feed."
    NumGestatingOnDay_4, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 4 more days before attempting to feed."
    NumGestatingOnDay_5, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 5 more days before attempting to feed."
    NumGestatingOnDay_6, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 6 more days before attempting to feed."
    NumGestatingOnDay_7, integer, "If **Include_Gestation_Columns** = 1, then this column contains the number of vectors that are gestating but with 7 more days before attempting to feed."
    VECTOR_WOLBACHIA_FREE, integer, "If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that are Wolbachia free."
    VECTOR_WOLBACHIA_A, integer, "If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that have Wolbachia A."
    VECTOR_WOLBACHIA_B, integer, "If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that have Wolbachia B."
    VECTOR_WOLBACHIA_AB, integer, "If **Include_Wolbachia_Columns** = 1, then this column contains the number of adult female vectors that have Wolbachia AB."
    XXX_AvailableHabitat, integer, "If **Stratify_By_Species** = 0, then this column title does not have the species name in it.  If **Stratify_By_Species** = 1, then there is a column for each species.  This column contains the number of larva that the habitat could add (e.g. number of spots open); equal to current capacity - current larval count."
    XXX_EggCrowdingCorrection, float, "If **Stratify_By_Species** = 0, then this column title does not have the species name in it.  If **Stratify_By_Species** = 1, then there is a column for each species.  This column contains the probability that eggs die due to overcrowding."
    HasMicrosporidia-STATE_XXX, integer, "If **Include_Microsporidia_Columns** = 1, then the columns contain number of vectors in that state that have microsporidia."
    NoMicrosporidia-STATE_XXX, integer, "If **Include_Microsporidia_Columns** = 1, then the columns contain number of vectors in that state that do not have microsporidia."



Example
=======

The following are examples of ReportVectorStats.csv files.  The examples do not include the Death By State columns.

This example includes Wolbachia columns:

.. csv-table::
    :header: STATE_ADULT,STATE_MALE,STATE_IMMATURE,STATE_LARVA,STATE_EGG,NewEggsCount,IndoorBitesCount,IndoorBitesCount-Infectious,OutdoorBitesCount,OutdoorBitesCount-Infectious,NewAdults,UnmatedAdults,DiedBeforeFeeding,DiedDuringFeedingIndoor,DiedDuringFeedingOutdoor,VECTOR_WOLBACHIA_FREE,VECTOR_WOLBACHIA_A,VECTOR_WOLBACHIA_B,VECTOR_WOLBACHIA_AB,MigrationFromCountLocal,MigrationFromCountRegional,arabiensis_AvailableHabitat,funestus_AvailableHabitat,gambiae_AvailableHabitat,arabiensis_EggCrowdingCorrection,funestus_EggCrowdingCorrection,gambiae_EggCrowdingCorrection,NumInfectousBitesGiven,NumInfectousBitesReceived,InfectiousBitesGivenMinusReceived
    :widths: 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5

    16220,36576,17593,147016,1541720,770860,8537,202,2426,75,1469,0,2788,844,245,0,137427,0,0,0,0,8991.45,4123.95,10026.9 0.00706801,0.0259187,0.00710855,277,136,141,0
    14635,34183,17098,152982,958640,479320,4756,479,1366,128,1047,0,2501,517,121,15087,0,0,0,0,0,3873.64,3814.74,4504.05,0.0133491,0.0316351,0.0135903,607,295,312
    13247,32339,12849,150692,1264080,632040,5812,296,1559,92,1339,0,2287,643,159,66443,0,0,0,0,0,3662.45,2833.68,4034.73,0.00908111,0.0593457,0.00962815,388,219,169
    12066,30731,14408,140976,1452320,726160,6700,270,1803,76,1564,0,2100,637,171,0,130007,0,0,0,0,8211.71,3889.12,9207.12,0.00671468,0.0242195,0.00670622,346,178,168
    12590,30509,10898,145816,794440,397220,4239,455,1166,129,2672,0,1969,466,134,15105,0,0,0,0,0,2797.77,3512.56,3192.74,0.0129099,0.0288083,0.0135152,584,274,310
    11243,28771,10887,138512,954720,477360,5676,312,1556,128,1134,0,1928,610,153,59130,0,0,0,0,6894.61,3493.81,7625.89,0.00798359,0.049113,0.00857158,440,227,213,0
    8933,26075,14491,138662,1112920,556460,5247,329,1429,92,0,0,1884,604,131,0,136952,0,0,0,0,14562.2,4190.82,16253.6,0.0172538,0.0315782,0.0171569,421,240,181
    9541,25515,9959,159705,705280,352640,2854,347,746,106,1965,0,1575,286,84,12354,0,0,0,0,0,1660.21,3321.22,2031.23,0.0308546,0.035052,0.031173,453,221,232
    8604,24184,14841,143138,946320,473160,5224,418,1312,111,1070,0,1549,552,130,4545,0,0,0,0,0,5737.64,3498.29,6278.16,0.00562629,0.0425362,0.00611594,529,250,279
    7951,22936,16030,140226,860880,430440,4290,310,1058,86,1048,0,1454,435,117,0,137234,0,0,0,0,3113.21,3527.66,3467.57,0.014121,0.0311236,0.0146823,396,208,188
    8216,22242,15596,132199,463280,231640,2584,344,685,109,1552,0,1391,299,68,15421,0,0,0,0,0,1562.56,3622.39,1707.29,0.00863056,0.0325911,0.00884764,453,214,239
    6553,20374,17428,122419,854320,427160,4512,421,1178,111,248,0,1482,490,140,63235,0,0,0,0,0,3282.25,3217.14,3811.39,0.00827453,0.0702558,0.00766011,532,263,269
    8015,21173,12487,118951,683640,341820,3003,376,741,94,2646,0,1204,346,76,0,136025,0,0,0,0,2047.61,3347.56,2169.57,0.00896889,0.0306045,0.00994518,470,233,237
    7913,20868,8126,115273,420600,210300,3489,299,927,70,1585,0,1298,357,82,14010,0,0,0,0,0,1894.64,2482.64,2145.04,0.00736232,0.0335831,0.0070938,369,172,197
    7560,20286,8209,107152,734040,367020,4018,384,1079,109,1393,0,1290,449,102,59413,0,0,0,0,0,2474.93,3355.48,2673.81,0.0110462,0.046009,0.0109935,493,241,252
    7525,19644,6876,103579,476880,238440,2978,375,665,90,1292,0,1279,323,61,0,125487,0,0,0,0,1868.86,3167.59,2158.96,0.00808167,0.0314773,0.00832445,465,218,247



This table includes gestation columns:

.. csv-table::
    :header: Time,NodeID,Population,VectorPopulation,STATE_INFECTIOUS,STATE_INFECTED,STATE_ADULT,STATE_MALE,STATE_IMMATURE,STATE_LARVA,STATE_EGG,NumLookingToFeed,NumFedCount,NumGestatingBegin,NumGestatingEnd,NumAttemptFeedIndoor,NumAttemptFeedOutdoor,NumAttemptButNotFeed,NewEggsCount,IndoorBitesCount,IndoorBitesCount-Infectious,OutdoorBitesCount,OutdoorBitesCount-Infectious,Unmated Adults,NewAdults,DiedBeforeFeeding,DiedDuringFeedingIndoor,DiedDuringFeedingOutdoor,NumGestatingOnDay_0,NumGestatingOnDay_1,NumGestatingOnDay_2,NumGestatingOnDay_3,NumGestatingOnDay_4,NumGestatingOnDay_5,NumGestatingOnDay_6,NumGestatingOnDay_7, arabiensis_AvailableHabitat,arabiensis_EggCrowdingCorrection
    :widths: 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5

    350,1,1000,88760,2171,16352,70237,100715,124862,1699008,1647000,29944,16393 ,48447,64840,8098,8154,11915,823500,8,1,8,0,0,12005,10422,820,816,9823,11150,12887,14587,16393,0,0,0,0,0 
    351,1,1000,88451,2127,16377,69947,100900,124843,1699680,1641840,29839,16278 ,48381,64659,8059,8021,11911,820920,8,0,8,1,0,11881,10540,848,802,9772,11285,12856,14468,16278,0,0,0,0,0 
    352,1,1000,88312,2110,16283,69919,100936,125391,1697598,1619120,29630,16020 ,48388,64408,7970,7859,12004,809560,7,2,7,2,0,11900,10433,803,803,9901,11347,12790,14350,16020,0,0,0,0,0 
    353,1,1000,88477,2117,16291,70069,101167,125234,1698069,1655960,29957,16285 ,48062,64347,8014,8127,12029,827980,8,1,8,0,0,12101,10293,807,836,9964,11265,12681,14152,16285,0,0,0,0,0 
    354,1,1000,88617,2154,16232,70231,101057,125605,1697983,1669440,30280,16509 ,47938,64447,8045,8214,12183,834720,8,0,8,0,0,11987,10259,790,798,9889,11158,12502,14389,16509,0,0,0,0,0 
    355,1,1000,88480,2154,16217,70109,101222,125573,1698350,1649840,30097,16393 ,47995,64388,8120,8083,12069,824920,8,0,8,1,0,12023,10525,813,822,9715,11030,12662,14588,16393,0,0,0,0,0 
  
    
This table includes microsporidia columns:

.. csv-table::
    :header: Time,NodeID,Population,VectorPopulation,STATE_INFECTIOUS,STATE_INFECTED,STATE_ADULT,STATE_MALE,STATE_IMMATURE,STATE_LARVA,STATE_EGG,NewEggsCount,IndoorBitesCount,IndoorBitesCount-Infectious,OutdoorBitesCount,OutdoorBitesCount-Infectious,NewAdults,UnmatedAdults,DiedBeforeFeeding,DiedDuringFeedingIndoor,DiedDuringFeedingOutdoor,NumDiedInfectious,NumDiedInfected,NumDiedAdults,NumDiedMale,AvgAgeAtDeathInfectious,AvgAgeAtDeathInfected,AvgAgeAtDeathAdults,AvgAgeAtDeathMale,AvgDurationLarvaeToImmature,HasMicrosporidia-STATE_INFECTIOUS,HasMicrosporidia-STATE_INFECTED,HasMicrosporidia-STATE_ADULT,HasMicrosporidia-STATE_MALE,HasMicrosporidia-STATE_IMMATURE,HasMicrosporidia-STATE_LARVA,HasMicrosporidia-STATE_EGG,NoMicrosporidia-STATE_INFECTIOUS,NoMicrosporidia-STATE_INFECTED,NoMicrosporidia-STATE_ADULT,NoMicrosporidia-STATE_MALE,NoMicrosporidia-STATE_IMMATURE,NoMicrosporidia-STATE_LARVA,NoMicrosporidia-STATE_EGG,SillySkeeter_AvailableHabitat,SillySkeeter_EggCrowdingCorrection
    :widths: 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5
    
    34,340461476,1000,8595,12,209,8374,10936,12679,81106,302440,151220,2603,0,0,0,1227,0,873,264,0,0,18,1119,1048,0,8.44444,5.95085,7.46183,11,0,0,0,0,0,0,0,12,209,8374,10936,12679,81106,302440,11593.8,0.0357489
    35,340461476,1000,8694,26,210,8458,11051,12616,81384,315720,157860,2713,1,0,0,1221,0,831,291,0,0,29,1093,1069,0,8.58621,6.36688,7.7521,11,0,0,0,0,0,0,0,26,210,8458,11051,12616,81384,315720,11437.7,0.0383342
    36,340461476,1000,8802,38,211,8553,11286,13262,80529,344080,172040,2841,4,0,0,1196,0,796,292,0,5,30,1053,1040,12.2,9.4,6.24691,7.78462,11,0,0,0,0,0,0,0,38,211,8553,11286,13262,80529,344080,12400.3,0.0362274
    37,340461476,1000,9000,46,215,8739,11420,13336,81294,337560,168780,2783,5,0,0,1246,0,761,287,0,4,26,1018,1109,14.5,10.3077,6.11002,8.17764,11,0,0,0,0,0,0,0,46,215,8739,11420,13336,81294,337560,11730.2,0.0360389
    38,340461476,1000,9140,50,229,8861,11428,13306,81547,343280,171640,2853,4,0,0,1300,0,855,305,0,6,18,1136,1173,16.6667,7.33333,6.70158,8.22677,11,0,0,0,0,0,0,0,50,229,8861,11428,13306,81547,343280,11561,0.03475
    39,340461476,1000,9177,58,226,8893,11535,13517,81669,359000,179500,2993,8,0,0,1186,0,846,303,0,4,30,1115,1068,14.75,10.3333,6.53453,8,11,0,0,0,0,0,0,0,58,226,8893,11535,13517,81669,359000,11512.9,0.0336779
    40,340461476,1000,9428,67,221,9140,11866,13201,81574,355160,177580,2847,5,0,0,1425,0,871,303,0,6,26,1142,1128,12.8333,9.69231,6.50613,8.34486,11,0,0,0,0,0,0,0,67,221,9140,11866,13201,81574,355160,11673.1,0.0320693
    41,340461476,1000,9510,73,224,9213,12055,13208,81606,365520,182760,3126,6,0,0,1260,0,876,302,0,8,26,1144,1143,15.875,8.76923,6.38112,8.55731,11,0,0,0,0,0,0,0,73,224,9213,12055,13208,81606,365520,11698.6,0.0328671



