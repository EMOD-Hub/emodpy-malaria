======================
IRSHousingModification
======================

The **IRSHousingModification** intervention class includes Indoor Residual Spraying (IRS) in the
simulation. IRS is another key vector control tool in which insecticide is sprayed on the interior
walls of a house so that mosquitoes resting on the walls after consuming a blood meal will die. IRS
can also have a repellent effect. Because this class is distributed to individuals, it can target
subgroups of the population. To target all individuals in a node, use
:doc:`parameter-campaign-node-indoorspacespraying`. Do not use **IRSHousingModification** and
**IndoorSpaceSpraying** together.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** No. Stacks by default, efficacies combine 1-(1-prob1)*(1-prob2)etc.
*  **Vector killing contributes to:** Indoor Die After Feeding
*  **Vector effects:** Repelling and killing
*  **Vector sexes affected:** Indoor meal-seeking females only
*  **Vector life stage affected:** Adult



.. include:: ../reuse/warning-housing-mods.txt

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-irshousingmodification.csv

.. literalinclude:: ../json/campaign-irshousingmodification.json
   :language: json