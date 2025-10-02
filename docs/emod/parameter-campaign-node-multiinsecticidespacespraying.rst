=============================
MultiInsecticideSpaceSpraying
=============================

The **MultiInsecticideSpaceSpraying** intervention class is a node-level intervention that models
the application of a multi-insecticide outdoor spray. As a spray, this kills male and female adult
and immature mosquitoes. Mosquitoes have a daily probability of dying; feeding status does not impact
the probability of death for adult female mosquitoes.

The effectiveness of the intervention is combined using the following equation:

Total efficacy = 1.0 – (1.0 – efficacy_1)* (1.0 – efficacy_2) * … * (1.0 – efficacy_n)


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes, especially when targeting certain species.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Uses PurgeExistingByName(). Adding a new intervention of this class will overwrite any existing intervention of the same class and Intervention_Name, however, if Intervention_Name is different, both interventions will coexist and their efficacies will combine.
*  **Vector killing contributes to:** Die Without Attempting to Feed & Die Before Attempting Human Feed
*  **Vector effects:** Killing
*  **Vector sexes affected:** Both males and females
*  **Vector life stage affected:** Adult and immature

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-multiinsecticidespacespraying.csv

.. literalinclude:: ../json/campaign-multiinsecticidespacespraying.json
   :language: json


