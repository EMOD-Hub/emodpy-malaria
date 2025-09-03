====================
HumanHostSeekingTrap
====================

The **HumanHostSeekingTrap** intervention class applies a trap that attracts and kills host-seeking
mosquitoes in the simulation. Human-host-seeking traps are individually-distributed interventions
that have attraction and killing rates that decay in an analogous fashion to the blocking and
killing rates of bednets.

An artificial diet diverts the vector from feeding on the human population, resulting in a two-fold
benefit:

#. The uninfected mosquitoes avoid biting infected humans some of the time, therefore decreasing the amount of human-to-vector transmission.
#. Infectious vectors are diverted to feed on artificial diet instead of humans, therefore decreasing the amount of vector-to-human transmission.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** No
*  **Time-based expiration:** No
*  **Purge existing:** Yes. Adding a new intervention of this class will overwrite any existing intervention of the same class in an individual. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Indoor Die Before Feeding
*  **Vector effects:** Artificial Diet feed instead of Human or Animal Feed
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult



.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-humanhostseekingtrap.csv

.. literalinclude:: ../json/campaign-humanhostseekingtrap.json
   :language: json
