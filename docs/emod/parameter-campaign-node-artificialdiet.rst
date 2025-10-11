==============
ArtificialDiet
==============

The **ArtificialDiet** intervention class is used to include feeding stations for vectors within a
node in a simulation. This is a node-targeted intervention and takes effect at the broad village
level rather than at the individual level. For individual-level effects, use
:doc:`parameter-campaign-individual-humanhostseekingtrap` instead. An artificial diet
diverts some of the vectors seeking to blood feed that day, resulting in a two-fold benefit:

#. The uninfected mosquitoes avoid biting infected humans some of the time, therefore
   decreasing the amount of human-to-vector transmission.

#. Infectious vectors are diverted to feed on the artificial diet instead of the humans, therefore
   decreasing the amount of vector-to-human transmission.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** No
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** No killing
*  **Vector effects:** Artificial Diet Feed instead of Human or Animal Feed
*  **Vector sexes affected:** Meal-seeking females only.
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-artificialdiet.csv

.. literalinclude:: ../json/campaign-artificialdiet.json
   :language: json