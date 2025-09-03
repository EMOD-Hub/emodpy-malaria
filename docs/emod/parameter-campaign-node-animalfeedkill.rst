==============
AnimalFeedKill
==============

The **AnimalFeedKill** intervention class imposes node-targeted mortality to a vector that
feeds on animals.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes, can be used to target sub-groups using genomes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes. Adding a new intervention of this class will overwrite any existing intervention of the same class in a node. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Die Before Attempting to Feed
*  **Vector effects:** Killing
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-animalfeedkill.csv

.. literalinclude:: ../json/campaign-animalfeedkill.json
   :language: json
