==========
Larvicides
==========

The **Larvicides** intervention class is a node-level intervention that configures a killing effect for larva
in specific habitats. This intervention can be used to simulate the application of larvicides to water bodies.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific genders.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** No. Stacks by default, efficacies combine 1-(1-prob1)*(1-prob2)etc.
*  **Vector killing contributes to:** Combines with competition and rainfall to kill larvae every time step.
*  **Vector effects:** Killing
*  **Vector sexes affected:** Both males and female larva
*  **Vector life stage affected:** Larval

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-larvicides.csv

.. literalinclude:: ../json/campaign-larvicides.json
   :language: json