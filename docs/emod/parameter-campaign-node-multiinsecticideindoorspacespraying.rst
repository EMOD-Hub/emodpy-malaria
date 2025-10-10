===================================
MultiInsecticideIndoorSpaceSpraying
===================================

The **MultiInsecticideIndoorSpaceSpraying** intervention class is a node-level intervention that
uses Indoor Residual Spraying (IRS) with multiple insecticides. It builds on the
:doc:`parameter-campaign-node-indoorspacespraying` class by allowing for multiple insecticides, each
with their own specified killing efficacy.

The effectiveness of the intervention is combined using the following equation:

Total efficacy = 1.0 – (1.0 – efficacy_1) * (1.0 – efficacy_2) * … * (1.0 – efficacy_n)


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target subgroups using genomes, especially when targeting certain species.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Indoor Die After Feeding
*  **Vector effects:** Killing
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-multiinsecticideindoorspacespraying.csv

.. literalinclude:: ../json/campaign-multiinsecticideindoorspacespraying.json
   :language: json
