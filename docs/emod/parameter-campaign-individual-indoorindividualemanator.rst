========================
IndoorIndividualEmanator
========================

The **IndoorIndividualEmanator** intervention class is a house modification intervention and it imitates the use of
personal mosquito repellents that are designed for indoor use, such as mosquito coils or vaporizer mats. These
interventions release insecticides into the air to repel or kill mosquitoes in the vicinity of the
individual using the emanator. The intervention is distributed to individuals, allowing for
targeting specific subgroups of the population.

The intervention acts on vectors seeking a blood meal indoors. Once the vectors is indoors, it is first
repelled based on the repelling effect. Then, the vectors that are not repelled, are subjected to the
killing effect. Vectors that are not repelled or killed can proceed to try to bite the individual and will
be subject to other individual indoor interventions. After the vectors have successfully fed (human or non-human meal),
the are subjected again to the killing effect of the emanator before exiting the indoor environment. Hence,
the IndoorIndividualEmanator can contribute to both Indoor Die Before Feeding and Indoor Die After Feeding.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. It can target specific species or other subgroups.
*  **Time-based expiration:** No
*  **Purge existing:** Yes. If a new intervention is added to to the individual, the existing intervention of the same class is removed when the new one is added.
*  **Vector killing contributes to:** Indoor Die Before Feeding, Indoor Die After Feeding
*  **Vector effects:** Repelling and killing
*  **Vector sexes affected:** Females seeking blood meal indoors only
*  **Vector life stage affected:** Adult



.. include:: ../reuse/warning-housing-mods.txt

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-indoorindividualemanator.csv

.. literalinclude:: ../json/campaign-indoorindividualemanator.json
   :language: json