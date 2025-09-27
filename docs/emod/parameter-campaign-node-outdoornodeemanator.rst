===================
OutdoorNodeEmanator
===================

The **OutdoorNodeEmanator** intervention class implements node-level outdoor emanators against blood meal-seeking
vectors. This imitates the use of outdoor insecticide sprays. These interventions release insecticides into the air
to repel or kill mosquitoes within the node. The intervention is distributed to nodes and affects all the
meal-seeking vectors in the node.

The intervention acts on vectors seeking a blood meal. The vectors are first repelled. First, the vectors are repelled.
The repelled vectors contribute to "survive without successful feed" number. The vectors that are not repelled, but are
affected by the intervention, depending on coverage, are subjected to the killing effect. Vectors that are not
repelled or killed can proceed to try find a meal indoors or outdoors, human and non-human and will be subject to
other interventions affecting meal-seeking vectors. After the vectors have successfully fed (indoor or outdoor,
human or non-human meal), the are subjected again to the killing effect of the emanator as the either exit the indoors
or remain outdoors after the meal. The OutdoorNodeEmanator contributes to "survive without successful feed",
"die before attempt human feed", and "die after feeding" statistics.

OutdoorNodeEmanator also affects entire male population of the node.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes. If a new intervention is added to to the node, the existing intervention of the same class is removed when the new one is added.
*  **Vector killing contributes to:** Survive Without Successful Feed, Die Before Attempt Human Feed, Die After Feeding, male vector daily mortality
*  **Vector effects:** Repelling, killing
*  **Vector sexes affected:** Females seeking blood-meal and all males
*  **Vector life stage affected:** Adult



.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-outdoornodeemanator.csv

.. literalinclude:: ../json/campaign-outdoornodeemanator.json
   :language: json
