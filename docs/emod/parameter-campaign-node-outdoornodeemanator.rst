===================
OutdoorNodeEmanator
===================

The **OutdoorNodeEmanator** intervention class implements node-level outdoor emanators against blood meal-seeking
vectors. This imitates the use of outdoor insecticide sprays. These interventions release insecticides into the air
to repel or kill mosquitoes within the node. The intervention is distributed to nodes and affects all the
meal-seeking vectors in the node.

The intervention acts on vectors seeking a blood meal. Vectors are repelled at final_repelling = coverage*repelling rate 
and final_killing = coverage * killing rate. The vectors that move to continue to seek the meal and are 
not repelled or killed are calculated using the following formula: (1 - coverage*repelling)(1-coverage*killing).
Please note that the killing affects all vectors that were not repelled by the intervention including those not affected by 
repelling due to coverage. These vectors can proceed to try find a meal indoors or outdoors, human and non-human and will be subject to
other interventions affecting meal-seeking vectors. After the vectors have successfully fed (indoor or outdoor,
human or non-human meal), the are subjected again to the killing effect of the emanator as they either exit the indoors
or remain outdoors after the meal. The OutdoorNodeEmanator contributes to "survive without successful feed",
"die before attempt human feed", and "die after feeding" statistics.

If there are multiple OutdoorNodeEmanators in the node (see **Purge existing** below), then the efficacies of the 
interventions are combined the following way: final_repelling = 1 - ( 1 - final_repelling)*(1-new_coverage*new_repelling)
and final_killing =  1 - ( 1 - final_killing)*(1-new_coverage*new_killing).

OutdoorNodeEmanator also affects entire male population of the node.



At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
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
