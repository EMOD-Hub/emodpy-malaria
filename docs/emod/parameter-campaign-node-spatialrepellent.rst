================
SpatialRepellent
================

The **SpatialRepellent** intervention class implements node-level spatial repellents exclusively against
outdoor-biting mosquitoes.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Uses PurgeExistingByName(). Adding a new intervention of this class will overwrite any existing intervention of the same class and Intervention_Name, however, if Intervention_Name is different, both interventions will coexist and their efficacies will combine.
*  **Vector killing contributes to:** No killing but Survive Without Successful Feed
*  **Vector effects:** Repelling
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult



.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-spatialrepellent.csv

.. literalinclude:: ../json/campaign-spatialrepellent.json
   :language: json
