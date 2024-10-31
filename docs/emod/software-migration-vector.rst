======================
Vector migration files
======================

Vector migration file describes the rate of migration of vectors *out* of a geographic :term:`node`
analogously to human migration (see :doc:`software-migration` for more information), although vector
migration supports gender parameters, it does not support migration by age and age-based migration 
in the migration file will cause an error. Vector migration is one way, such that each trip made by
a vector is independent of previous trips made by the vector. For **Vector_Sampling_Type** set to 
"TRACK_ALL_VECTORS" or "SAMPLE_IND_VECTORS", the rates in the file are used to control whether or not 
a female vector will migrate: the rate specified is used to get a "time to leave on trip" value
from an exponential distribution. If the value is less than one day, then the female vector will migrate.
For male vectors (who are always in cohorts/compartments), and for female vectors when 
**Vector_Sampling_Type** is set to "VECTOR_COMPARTMENTS_NUMBER" or "VECTOR_COMPARTMENTS_PERCENT", 
the rates in the file are used to calculate what fraction of the population is traveling out of the node
on that day based on a total rate of travel out of that node and the traveling vectors are distributed 
to their destination nodes in proportion of rates to those nodes to the total outbound rate. 

If default geography is used (the configuration parameter **Enable_Demographics_Builtin** is set to 1, 
and **Default_Geography_Initial_Node_Population** and **Default_Geography_Torus_Size** are configured), 
vector migration will be built internally and vectors will automatically migrate. It is a known issue,
please see https://github.com/InstituteforDiseaseModeling/EMOD/issues/43

Vectors "LOCAL_MIGRATION" MigrationType for all their migration needs, but are not limited to the default 
maximum data values of 8 (destinations).

Each vector species has its own **Vector_Migration_Filename**, if it is left as an empty string, no 
migration will happen for that species. The **Vector_Migration_Modifier_Equation** and its parameters 
can influence female vector migration to particular nodes over others, while **x_Vector_Migration** is
a multiplier affects the migration rates for both genders. See :doc:`parameter-configuration` for more
information on the parameters governing vector migration.

Migration Files
==================

Vectors use the same migration files as humans, with two caveats:

1. Vectors do not migrate by-age, so multiple AgeBins in the by-age by-gender migration file will cause an error.
2. Vector migration only uses MigrationType "LOCAL_MIGRATION" all other migration types will cause an error.
