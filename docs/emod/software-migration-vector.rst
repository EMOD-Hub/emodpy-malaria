=================
Vector migration
=================

The vector migration file describes the rate of migration of vectors *out* of a geographic :term:`node`
analogously to human migration (see :doc:`software-migration` for more information). The vector
model does not support migration by age and age-based migration in the migration file will cause an
error, but does support migration by vector gender as well as migration based on genetics (see below).
Vector migration is one way, such that each trip made by a vector is independent of previous trips made
by the vector.

Note: If default geography is used (the configuration parameter **Enable_Demographics_Builtin** is set to 1,
and **Default_Geography_Initial_Node_Population** and **Default_Geography_Torus_Size** are configured), 
vector migration will be built internally and vectors will automatically migrate.

Vectors do not have a "MigrationType" as each species uses only one file for all their migration needs.

Each vector species has its own **Vector_Migration_Filename**; if it is left as an empty string, no
migration will happen for that species. The **Vector_Migration_Modifier_Equation** and its parameters 
can influence female vector migration to particular nodes over others, while **x_Vector_Migration** is
a multiplier that affects the migration rates for both genders. See :doc:`parameter-configuration` for more
information on the parameters governing vector migration.


Vector Migration Using Genetics
===============================

Vectors have a type of migration not available to humans set with **GenderDataType** = VECTOR_MIGRATION_BY_GENETICS in the
migration metadata file (usually a .bin.json file).

For information, see :ref:`migration_vector_genetics`.


Vector Migration Files
======================

The Binary file structure for the vector migration files is the same as it is for human files.
The Allele_Combinations array, when present for vector VECTOR_MIGRATION_BY_GENETICS, is used in the same capacity as
AgesYears array would be to maintain the same structure of the file. Please see :doc:`software-migration-creation`
for more details.

.. toctree::
   :maxdepth: 3
   :titlesonly:

   software-migration-creation-vector
