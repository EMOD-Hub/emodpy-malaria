====================================
How to create vector migration files
====================================

You can create the JSON metadata and binary migration files needed by |EMOD_s| to run simulations
from CSV ata using Python scripts provided by |IDM_s|. You can assign the same
probability of migration to each vector in a node or you can assign different migration rates based on gender or
genetics of the vector.

.. note:: 

    The **IdReference** must match the value in the demographics file. Each node can be connected a
    maximum of 100 destination nodes. The bin.json metadata file will be created without a valid
    **IdReference** with expectations that the user will set it themselves.


Create from CSV input
=====================

This script converts a CSV formatted txt file to an EMOD binary-formatted migration file.
It also creates the required metadata file.

The CSV file can have several column configurations:

1.  Header (optional):  FromNodeID, ToNodeID, Rate (Average # of Trips Per Day)
If the csv/text file has three columns with no headers, this is the format we assume.
This can be used for human and vector migration. The Rate is for any/all agents regardless of sex or age.

2.  Header (optional):  FromNodeID, ToNodeID, RateMales, RateFemales
If the csv/text file has four columns with no headers, this is the format we assume.
RateMales are rates for male migration, RateFemales for female migration and are Average # of Trips Per Day.

3.  Header (required):  FromNodeID, ToNodeID, [], arrays denoting Allele_Combinations
Allele_Combinations example: [["a1", "a1"], ["b1", "b1"]];  [["X1","Y2"]]; [["*", "a0"], ["X1", "Y1"]]
Due to use of commas in headers, it is best to use Excel to create them (or look at a sample text csv).
This is to support VECTOR_MIGRATION_BY_GENETICS. Headers are required for this csv file.
The first (empty, []) array is used as a "default rate" if the vector's genetics doesn't match any of the
Allele_Combinations. The other column headers denote the rate that the vector will travel at if it matches the
Allele_Combination listed. Vectors are checked against Allele_Combinations from most-specific, to least-specific,
regardless of the order in the csv file. Allele_Combinations can, but don't have to, include sex-alleles. Without
specified sex-alleles, any vector that matches the alleles regardless of sex will travel at that rate.

The FromNodeIDs and ToNodeIDs are the external ID's found in the demographics file.
Each node ID in the migration file must exist in the demographics file.
One can have node ID's in the demographics that don't exist in the migration file.

The CSV file does not have to have the same number of entries for each FromNodeID.
The script will find the FromNodeID that has the most and use that for the
DestinationsPerNode. The binary file will have DestinationsPerNode entries
per node.

#.  Run the `convert_csv_to_bin_vector_migration.py <https://github.com/InstituteforDiseaseModeling/EMOD/blob/master/Scripts/MigrationTools/convert_csv_to_bin_vector_migration.py>`_ script using the command format below::

        python convert_csv_to_bin_vector_migration.py [input-migration-csv]


This will create both the metadata and binary file needed by |EMOD_s|. 

Example Input files
-------------------

.. literalinclude:: ../csv/vector-migration-by-genetics-input.csv
.. literalinclude:: ../csv/vector-migration-by-sex-input.csv


JSON metadata file
==================

The metadata file is a JSON-formatted file that includes a metadata section and a node offsets
section. The **Metadata** section contains a JSON object with parameters, some of which are
strictly informational and some of which are used by |exe_s|. However, the informational ones may
still be important to understand the provenance and meaning of the data.

Vector Migration Metadata File Parameters
------------------------------------------

Vector migration does not do age-based migration and does not differentiate the migration type since there
is only one migration file per species, therefore the parameters pertaining to those options are not included,
and if included, are ignored. The omitted parameters are: MigrationType, AgesYears, InterpolationType.

The following parameters can be included in the by-gender or by-genetics migration metadata file:

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 10,5,20

    IdReference, string, "(Used by |EMOD_s|.) A unique, user-selected string that indicates the method used by |EMOD_s| for generating **NodeID** values in the input files. For more information, see :doc:`software-inputs`."
    DateCreated, string, Date and time the file was generated.
    Tool, string, The script used to create the file.
    DatavalueCount, integer, "(Used by |EMOD_s|.) The number of outbound data values per node (max 100). The number must be the same across every node in the binary file."
    GenderDataType, enum, "Denotes whether data is provided for each gender separately, is the same for both, or depends on vector genetics. Accepted values are ONE_FOR_BOTH_GENDERS, ONE_FOR_EACH_GENDER, VECTOR_MIGRATION_BY_GENETICS."
    AlleleCombinations, array, "An array of Allele_Combinations, starting with an emtpy array to mark the default migration rate."
    NodeCount, integer, "(Used by |EMOD_s|.) The number of nodes to expect in this file."
    NodeOffsets, string, "(Used by |EMOD_s|.) A string that is **NodeCount** :math:`\times` 16 characters long. For each node, the first 8 characters are the origin **NodeID** in hexadecimal. The second 8 characters are the byte offset in hex to the location in the binary file where the destination **NodeIDs** and migration rates appear."


Example
-------

.. literalinclude:: ../json/vector-migration-metadata.json
   :language: json



