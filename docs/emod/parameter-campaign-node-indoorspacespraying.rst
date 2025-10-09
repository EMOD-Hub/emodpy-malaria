===================
IndoorSpaceSpraying
===================

The **IndoorSpaceSpraying** intervention class is a node-level vector control mechanism that works
by spraying insecticides indoors. This class is similar to to
:doc:`parameter-campaign-individual-irshousingmodification` but **IRSHousingModification** is an
individual-level intervention that uses both killing and blocking effects and
**IndoorSpaceSpraying** is a node-level intervention that uses only a killing effect. Do not use
these two interventions together. If used with **IRSHousingModification**, the **IndoorSpaceSpraying** will
override **IRSHousingModification**'s killing effect.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes, especially when targeting certain species.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die After Feeding, Indoor Die Before Feeding (when in combination with HumanHostSeekingTrap)
*  **Vector effects:** Killing
*  **Vector sexes affected:** Indoor meal-seeking females only
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-indoorspacespraying.csv

.. literalinclude:: ../json/campaign-indoorspacespraying.json
   :language: json