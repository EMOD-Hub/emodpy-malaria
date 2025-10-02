===================================
SpatialRepellentHousingModification
===================================

The **SpatialRepellentHousingModification** intervention class is a housing modification utilizing
spatial repellents. The protection provided by this intervention is exclusively against
indoor-biting mosquitoes.

At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, when it has been distributed to individuals.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific vectors.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** No. Stacks by default, efficacies combine 1-(1-prob1)*(1-prob2)etc.
*  **Vector killing contributes to:** No killing.
*  **Vector effects:** Repelling.
*  **Vector sexes affected:** Indoor meal-seeking females only
*  **Vector life stage affected:** Adult

.. include:: ../reuse/warning-housing-mods.txt

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-spatialrepellenthousingmodification.csv

.. literalinclude:: ../json/campaign-spatialrepellenthousingmodification.json
   :language: json