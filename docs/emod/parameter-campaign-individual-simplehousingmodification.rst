=========================
SimpleHousingModification
=========================

The **SimpleHousingModification** intervention class implements a generic housing modification for
vector control. It is the base class from which other housing modifications are derived.

At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, when it has been distributed to individuals.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific vectors.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** No. Already existing intervention(s) of this class continue(s) to exist together with any new interventions of this class. Their efficacies combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Before Feeding, Die After Feeding, Host Not Available
*  **Vector effects:** Repelling, Killing.
*  **Vector sexes affected:** Indoor meal-seeking females
*  **Vector life stage affected:** Adult

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-simplehousingmodification.csv

.. literalinclude:: ../json/campaign-simplehousingmodification.json
   :language: json