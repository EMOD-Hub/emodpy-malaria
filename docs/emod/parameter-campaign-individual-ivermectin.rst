==========
Ivermectin
==========

The **Ivermectin** intervention class modifies the feeding outcome probabilities for both indoor-
and outdoor-feeding mosquitoes. Ivermectin works by increasing the mortality of mosquitoes after they
blood-feed on a human. It is an individually-distributed intervention that configures the waning of
the drug's killing effect on the adult mosquito population. This intervention enables exploration of
the impact of giving humans an insecticidal drug, and how the effectiveness and duration of the
drug's killing-effect interacts with other interventions. For example, you can look at the impact of
controlling and eliminating malaria transmission using both anti-parasite drugs that clear existing
infections and insecticidal drugs.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No, but it will expire if the efficacy is below 0.00001.
*  **Purge existing:** No. Stacks by default, efficacies combine 1-(1-prob1)*(1-prob2)etc.
*  **Vector killing contributes to:** Indoor/Outdoor Die After Feeding
*  **Vector effects:** Killing
*  **Vector sexes affected:** Meal-seeking females only
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-ivermectin.csv

.. literalinclude:: ../json/campaign-ivermectin.json
   :language: json
