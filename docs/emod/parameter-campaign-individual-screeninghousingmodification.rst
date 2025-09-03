============================
ScreeningHousingModification
============================

The **ScreeningHousingModification** intervention class implements housing screens as a vector
control effort. Housing screens are used to decrease the number of mosquitoes that can enter indoors
and therefore reduce indoor biting.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** Yes. If the Intervention_Name values are the same. Interventions of this class with different Intervention_Name values will co-exist in an individual.
*  **Vector killing contributes to:** Indoor After Feeding
*  **Vector effects:** Repelling and killing
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-housing-mods.txt

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-screeninghousingmodification.csv

.. literalinclude:: ../json/campaign-screeninghousingmodification.json
   :language: json