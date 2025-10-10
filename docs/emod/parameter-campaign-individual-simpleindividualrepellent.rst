=========================
SimpleIndividualRepellent
=========================

The **SimpleIndividualRepellent** intervention class provides protection to individuals against both
indoor-feeding and outdoor-feeding mosquito bites.

At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, when it has been distributed to individuals.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific vectors.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** No killing
*  **Vector effects:** Repelling.
*  **Vector sexes affected:** All meal-seeking females
*  **Vector life stage affected:** Adult

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-simpleindividualrepellent.csv

.. literalinclude:: ../json/campaign-simpleindividualrepellent.json
   :language: json