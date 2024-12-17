====================================
How to create vector migration files
====================================

You can create the JSON metadata and binary migration files needed by |EMOD_s| to run simulations
from CSV data using Python script below. You can assign the same probability of migration to
each vector in a node or you can assign different migration rates based on gender or genetics of the vector.

#.  Run the `convert_csv_to_bin_vector_migration.py <https://github.com/EMOD-Hub/emodpy-malaria/blob/main/emodpy_malaria/migration/convert_csv_to_bin_vector_migration.py>`_ script using the format below:

        python convert_csv_to_bin_vector_migration.py [input-migration-csv]


.. note:: 

    The **IdReference** must match the value in the demographics file. The bin.json metadata file will be created without a valid
    **IdReference** with expectations that the user will set it themselves.


CSV Input Configurations
========================
Below are different csv file input configurations you can use to create vector migration.

One rate for all vectors
------------------------

Header (optional):  FromNodeID, ToNodeID, Rate (Average # of Trips Per Day)
If the csv/text file has three columns with no headers, this is the format we assume.

.. csv-table::
    :header: Parameter, Data type,  Min, Max, Default, Description
    :widths: 10,5,5,5,5,20

    FromNodeID, integer, 1, 2147480000, NA,"NodeID, matching NodeIDs in demographics file, from which the vector/human will travel."
    ToNodeID, integer, 1, 2147480000, NA,"NodeID, matching NodeIDs in demographics file, to which the vector/human will travel."
    Rate, float, 0, 3.40282e+38, NA, "Rate at which the all the vectors/humans will travel from the FromNodeID to ToNodeID."

Example:

.. csv-table::
    :header: FromNodeID, ToNodeID, Rate
    :widths: 5,5,5

    5,1,0.1
    5,2,0.1
    5,3,0.1
    5,4,0.1
    5,6,0
    5,7,0
    5,8,0.1
    5,9,0.1

Actual csv:

.. literalinclude:: ../csv/migration-input-file-simple.csv


Different rates for male and female vectors
-------------------------------------------

Header (optional):  FromNodeID, ToNodeID, RateMales, RateFemales
If the csv/text file has four columns with no headers, this is the format we assume.

.. csv-table::
    :header: Parameter, Data type,  Min, Max, Default, Description
    :widths: 10,5,5,5,5,20

    FromNodeID, integer, 1, 2147480000, NA, "NodeID, matching NodeIDs in demographics file, from which the vector/human will travel."
    ToNodeID, integer, 1, 2147480000, NA,"NodeID, matching NodeIDs in demographics file, to which the vector/human will travel."
    RateMales, float,0, 3.40282e+38, NA,  "Rate at which the vector/human of male sex will travel from the FromNodeID to ToNodeID."
    RateFemales, float, 0, 3.40282e+38, NA, "Rate at which the vector/human of female sex will travel from the FromNodeID to ToNodeID."

Example:

.. csv-table::
    :header: FromNodeID, ToNodeID, RateMales, RateFemales
    :widths: 5,5,5,5

    5,1,0.1,0.02
    5,2,0.1,0.02
    5,3,0.1,0.02
    5,4,0.1,0.02
    5,6,0,0.02
    5,7,0,0.02
    5,8,0.1,0
    5,9,0.1,0

Actual csv:

.. literalinclude:: ../csv/vector-migration-by-sex-input.csv


Different rates depending on genetics of the vector
---------------------------------------------------

Header (required):  FromNodeID, ToNodeID, [], arrays denoting Allele_Combinations
Allele_Combinations example: [["a1", "a1"], ["b1", "b1"]] or  [["X1","Y2"]] or [["*", "a0"], ["X1", "Y1"]]
Due to use of commas in headers, it is best to use Excel to create them (or look at a sample text csv).
This is to support VECTOR_MIGRATION_BY_GENETICS. Headers are required for this csv file.
The first (empty, []) array is used as a "default rate" if the vector's genetics doesn't match any of the
Allele_Combinations. The other column headers denote the rate that the vector will travel at if it matches the
Allele_Combination listed. Vectors are checked against Allele_Combinations from most-specific, to least-specific,
regardless of the order in the csv file. Allele_Combinations can, but don't have to, include sex-alleles. Without
specified sex-alleles, any vector that matches the alleles regardless of sex will travel at that rate. Use '*' as a
wildcard if the second allele does not matter and can be matched with anything.

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 10,5,5,5,5,20

    FromNodeID, integer, 1, 2147480000, NA, "NodeID, matching NodeIDs in demographics file, from which the vector/human will travel."
    ToNodeID, integer, 1, 2147480000, NA, "NodeID, matching NodeIDs in demographics file, to which the vector/human will travel."
    [], float, 0, 3.40282e+38, NA, "Default rate at which the vector that doesn't match any other allele combinations will travel from the FromNodeID to ToNodeID."
    User-defined Allele Combination, float, 0, 3.40282e+38, NA, "Rate at which the vector that matches this and not a more-specific allele combination will travel from the FromNodeID to ToNodeID."

Example:

.. csv-table::
    :header: FromNodeID, ToNodeID, [], "[['a1', 'a1'], ['b1', 'b1']]", "[['*', 'a0'], ['X1', 'Y1']]", "[['X1','Y2']]"
    :widths: 5,5,5,5,5,5

    5,1,0.1,0,0,0
    5,2,0,0.1,0,0
    5,3,0,0,0.1,0
    5,4,0,0,0,0.1
    5,6,0,0,0,0
    5,7,0.1,0.1,0,0
    5,8,0.1,0,0.1,0.05
    5,9,0,0.1,0,0
    1,2,1,0,0,0
    1,3,0,1,0,0
    1,4,0,0,1,0
    1,6,0,0,0,1
    3,6,0,0,0,0
    3,7,0,0.5,0,0
    3,8,0.5,0,0,0.0
    3,9,0,0.5,0,0


Actual csv:

.. literalinclude:: ../csv/vector-migration-by-genetics-input.csv


Migration binary file
=====================

For information, see :ref:`binary_migration_file`.


JSON metadata file
==================

The metadata file is a JSON-formatted file that includes a metadata section and a node offsets
section. The **Metadata** section contains a JSON object with parameters that help |EMOD_s| interpret the migration
binary file. The users are encouraged to add their own parameters to the section to remind themselves about the source,
reason, purpose of the binary file and the data it contains. Non-required parameters are ignored.


Vector Migration Metadata File Parameters
------------------------------------------

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 10,5,20

    IdReference, string, "Required. A unique id to match demographics, climate, and migration files that work together."
    DatavalueCount, integer, "Required.The number of outbound data values per node (max 100). The number must be the same across every node in the binary file."
    GenderDataType, enum, "Required. Denotes whether data is provided for each gender separately, is the same for both, or depends on vector genetics. Accepted values are ONE_FOR_BOTH_GENDERS, ONE_FOR_EACH_GENDER, VECTOR_MIGRATION_BY_GENETICS."
    AlleleCombinations, array, "Required for GenderDataType: VECTOR_MIGRATION_BY_GENETICS. An array of Allele_Combinations, starting with an emtpy array to mark the default migration rate."
    NodeCount, integer, "Required. The number of 'from' nodes in the data. Used to verify size NodeOffsets - 16*NodeCount = # chars in NodeOffsets."
    NodeOffsets, string, "Required. The number of rates/'to' nodes for each 'from' node. Max of 100."
    DateCreated, string, Date and time the file was generated by the script. Informational for user only.
    Tool, string, The script used to create the file. Informational for user only.
    Project, string, Example of a user-created parameter. Informational for user only.


Example
-------

.. literalinclude:: ../json/vector-migration-metadata.json
   :language: json



