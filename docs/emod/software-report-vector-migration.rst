=====================
ReportVectorMigration
=====================

The vector migration report (ReportVectorMigration.csv) provides detailed information on when and
where vectors are migrating. As there will be one line for each migrating vector or cohort, it is 
beneficial to use the parameters to limit the size of the output file. 

See :doc:`software-migration-vector` for more information on how to create vector migration files.


Configuration
=============

To generate the report, configure the following parameters in the custom_reports.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **End_Day**, float, 0, 3.40E+38, 3.40E+38, "The day to stop collecting data for the report."
    **Start_Day**, float, 0, 3.40E+38, 0, The day to start collecting data for the report.
    **Species_List**, array of strings, NA, NA, [ ], "The species for which to include information. If the list is empty or absent, then data for all species will be collected."
    **Must_Be_In_State**, array of enums, NA, NA, [ ], "A list of vector states for which you want to record the migration. Only STATE_MALE, STATE_ADULT, STATE_INFECTED, STATE_INFECTIOUS migrate."
    **Must_Be_From_Node**, array of integers, 1, 2147480000, [ ], "A list of node IDs. A vector must be travelling FROM one of these nodes to be recorded into the report. Empty list means vectors traveling from any/all nodes will be recorded."
    **Must_Be_To_Node**, array of integers, 1, 2147480000, [ ], "A list of node IDs. A vector must be travelling TO one of these nodes to be recorded into the report. Empty list means vectors traveling from any/all nodes will be recorded."
    **Include_Genome_Data**, boolean, NA, NA, 0, "If set to true (1), adds a Genome column for migrating vectors. Vectors with no custom alleles will still have their sex alleles listed."
    **Filename_Suffix**, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
    

.. code-block:: json

    {
        "Reports": [
            {
                "class": "ReportVectorMigration",
                "Start_Day": 366.0,
                "End_Day": 375.0,
                "Include_Genome_Data": 1,
                "Must_Be_In_State": ["STATE_INFECTIOUS", "STATE_INFECTED"],
                "Must_Be_From_Node": [23, 24],
                "Must_Be_To_Node": [23, 24],
                "Species_List": [
                    "funestus"
                ],
                "Filename_Suffix": "funestus"
            },
        ],
        "Use_Defaults": 1
    }




Report structure and data channel descriptions
==============================================

The file contains the following data channels:

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 10, 20

    Time, integer, "The day that the vector migrated."
    ID, integer, "The ID of the vector or cohort.  Note that when using the cohort model, a cohort may need to split such that some of the cohort migrates to the node and some do not, creating new cohort IDs. This may make it difficult to follow cohorts by ID."
    FromNodeID, integer, "The ID of the node that the vector was migrating from."
    ToNodeID, integer, "The ID of the node that the vector traveled to."
    State, string, "The state of the migrating vector."
    Species, string, "The name of the species of vector."
    Age, integer, "The number of days the vector has been alive."
    Genome, string, "Full genome of the migrating vector."
    Population, integer, "The number of migrating vectors per line depends on the **Vector_Sampling_Type** setting. If **Vector_Sampling_Type** is set to TRACK_ALL_VECTORS or SAMPLE_INDIVIDUAL_VECTORS, female vectors migrate individually, so this number will always be 1. For male vectors, or for female vectors when **Vector_Sampling_Type** is set to VECTOR_COMPARTMENTS_NUMBER or VECTOR_COMPARTMENTS_PERCENT, the number can be greater than 1. This indicates that 'X' vectors of the same age, state, genome, and species are migrating between the specific nodes."


Example
=======

The following is an example of ReportVectorMigration.csv:

.. csv-table::
    :header: Time, ID, FromNodeID, ToNodeID, State, Genome, Species, Age, Population
    :widths: 10, 10, 10, 10, 10, 10, 10, 10, 10

    400, 220742554, 1487745020, 1487810556, STATE_INFECTED, X:X, arabiensis, 29, 10
    400, 211244943, 1487745020, 1487679485, STATE_INFECTIOUS, X:X, arabiensis, 34, 10
    400, 256543649, 1487745020, 1487810555, STATE_ADULT, X:X, arabiensis, 3, 10
    400, 259247278, 1487745020, 1487745019, STATE_MALE, X:Y, funestus, 0, 5
    400, 259248701, 1487745020, 1487810557, STATE_MALE, X:Y, funestus, 0, 2
    400, 259250124, 1487745020, 1487810556, STATE_MALE, X:Y, funestus, 0, 2
    400, 259251547, 1487745020, 1487679484, STATE_MALE, X:Y, funestus, 0, 1
    400, 259252970, 1487745020, 1487679485, STATE_MALE, X:Y, funestus, 0, 1
