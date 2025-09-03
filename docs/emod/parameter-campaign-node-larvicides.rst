==========
Larvicides
==========

The **Larvicides** intervention class is a node-level intervention that configures habitat reduction
for mosquito breeding sites that are poisoned by larvicides. This intervention accommodates sprayed
areas and vector-transported larvicides where resting surfaces may be treated not just with
:doc:`parameter-campaign-individual-irshousingmodification` to kill mosquitoes, but also with
particles that can be dispersed by mosquitoes to poison larval development sites. In particular, a
relatively small fraction of resting events may result in a relatively large fraction of larval
habitat.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. The vector genome can be used to target specific genders.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** Yes. Adding a new intervention of this class will overwrite any existing intervention of the same class in a node. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Combines with competition and rainfall to kill larvae every time step.
*  **Vector effects:** Killing
*  **Vector sexes affected:** Both males and females
*  **Vector life stage affected:** Larval

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-larvicides.csv

.. literalinclude:: ../json/campaign-larvicides.json
   :language: json