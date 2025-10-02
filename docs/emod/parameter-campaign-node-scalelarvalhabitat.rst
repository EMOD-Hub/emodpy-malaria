==================
ScaleLarvalHabitat
==================

The **ScaleLarvalHabitat** intervention class is a node-level intervention that enables
species-specific habitat modification within shared habitat types. This intervention has a similar
function to the demographic parameter **ScaleLarvalMultiplier**, but enables habitat availability to
be modified at any time or at any location during the simulation, as specified in the campaign
event.

To reset the multiplier, you must either replace the existing one with a new intervention with the same
Intervention_Name where the multiplier/factor is 1.0 or use the **Disqualifying_Properties** to cause the
intervention to abort.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** No
*  **Time-based expiration:** No. It will continue to exist even if the efficacy is zero.
*  **Purge existing:** Yes and No. Uses PurgeExistingByName(). Adding a new intervention of this class will overwrite any existing intervention of the same class and Intervention_Name, however, if Intervention_Name is different, both interventions will coexist and their efficacies will combine.
*  **Vector killing contributes to:** Does not apply
*  **Vector effects:** Does not apply
*  **Vector sexes affected:** both
*  **Vector life stage affected:** eggs and larva, depending on oviposition settings

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-scalelarvalhabitat.csv

.. literalinclude:: ../json/campaign-scalelarvalhabitat.json
   :language: json
