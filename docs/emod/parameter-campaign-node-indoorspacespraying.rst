===================
IndoorSpaceSpraying
===================

The **IndoorSpaceSpraying** intervention class is a node-level vector control mechanism that works
by spraying insecticides indoors. This class is similar to to
:doc:`parameter-campaign-individual-irshousingmodification` but **IRSHousingModification** is an
individual-level intervention that uses both killing and blocking effects and
**IndoorSpaceSpraying** is a node-level intervention that uses only a killing effect. Do not use
these two interventions together.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes, especially when targeting certain species.
*  **Time-based expiration:** No
*  **Purge existing:** Yes. Adding a new intervention of this class will overwrite any existing intervention of the same class in a node. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Indoor Die After Feeding
*  **Vector effects:** Killing
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-indoorspacespraying.csv

.. literalinclude:: ../json/campaign-indoorspacespraying.json
   :language: json