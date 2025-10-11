===============
OutdoorRestKill
===============

The **OutdoorRestKill** intervention class imposes node-targeted mortality to a vector that is at
rest in an outdoor environment after a feed. This affects vectors that have fed indoors and outdoors.
This also affects male vectors.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No. It will need to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes or specific sexes.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Outdoor Die After Feeding. Note that it is a node-level intervention but does not impact the other node-level probabilities.
*  **Vector effects:** Killing
*  **Vector sexes affected:** Males and meal-seeking females
*  **Vector life stage affected:** Adults


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-outdoorrestkill.csv

.. literalinclude:: ../json/campaign-outdoorrestkill.json
   :language: json