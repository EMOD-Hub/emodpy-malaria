=============
SpaceSpraying
=============

The **SpaceSpraying** intervention class implements node-level vector control by spraying pesticides
outdoors. This intervention targets specific habitat types, and imposes a mortality rate on all
targeted (both immature and adult male and female) mosquitoes. All mosquitoes have daily mortality
rates; mortality for adult females due to spraying is independent of whether or not they are
feeding.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No. You need to redistribute when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes, especially if you want to target specific sexes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Without Attempting To Feed & Die Before Attempting Human Feed
*  **Vector effects:** Killing
*  **Vector sexes affected:** Males and females
*  **Vector life stage affected:** Adult and immature



.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt


.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-spacespraying.csv

.. literalinclude:: ../json/campaign-spacespraying.json
   :language: json