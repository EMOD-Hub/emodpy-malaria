===============
OvipositionTrap
===============

The **OvipositionTrap** intervention class utilizes an oviposition trap to collect host-seeking mosquitoes, and
is based upon imposing a mortality to egg hatching from oviposition. This is a node-targeted
intervention and affects all mosquitoes living and feeding at a given node. This trap requires the
use of individual mosquitoes in the simulation configuration file (**Vector_Sampling_Type** must be
set to TRACK_ALL_VECTORS or SAMPLE_IND_VECTORS), rather than the cohort model. See :doc:`parameter-configuration-sampling`
configuration parameters for more information.

Notes and tips for this intervention:

*  It calculates a habitat-weighted average based on the current capacity of the habitat.  It then
   uses this average to determine if the vector dies while laying eggs.
*  A vector only lays eggs on the day she feeds.
*  In the individual model, each vector has its own timer indicating when it should feed.  If the
   number of days between feeds is configured to be temperature dependent
   (using the configuration parameter **Temperate_Dependent_Feeding_Cycle**), this duration can be
   different for each feed.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** No
*  **Time-based expiration:** No. It will continue to exist even if the efficacy is zero.
*  **Purge existing:** Yes. Adding a new intervention of this class will overwrite any existing intervention of the same class in a node. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Die Laying Eggs
*  **Vector effects:** Killing
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-ovipositiontrap.csv

.. literalinclude:: ../json/campaign-ovipositiontrap.json
   :language: json
