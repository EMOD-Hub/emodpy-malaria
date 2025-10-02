=========
SugarTrap
=========

The **SugarTrap** intervention class implements a vector sugar-baited trap to collect/kill
sugar-feeding mosquitoes and is sometimes called an attractive toxic sugar bait (ATSB). This
intervention affects all mosquitoes living and feeding at a given node. Male vectors sugar-feed
daily and female vectors sugar-feed once per blood meal (or upon emergence), so these traps can
impact male survival on a daily basis. Efficacy can be modified using per-sex insecticide
resistance.

The impact of sugar-baited traps will depend on the sugar-feeding behavior specified in the
configuration file via **Vector_Sugar_Feeding_Frequency**, whether there is no sugar feeding, sugar
feeding occurs once at emergence, sugar feeding occurs once per blood meal, or sugar feeding occurs
every day. Note that if it is set to VECTOR_SUGAR_FEEDING_NONE, this intervention will have no
effect. See :doc:`parameter-configuration-vector-control` configuration parameters for more
information.


At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No. It will need to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes or specific sexes.
*  **Time-based expiration:** Yes. Expiration time can be specified using specific distributions.
*  **Purge existing:** Yes and No. Uses PurgeExistingByName(). Adding a new intervention of this class will overwrite any existing intervention of the same class and Intervention_Name, however, if Intervention_Name is different, both interventions will coexist and their efficacies will combine.
*  **Vector killing contributes to:** Sugar Trap Killing
*  **Vector effects:** Killing
*  **Vector sexes affected:** Males and females
*  **Vector life stage affected:** Adult and immature when they are emerging (if configured)


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-sugartrap.csv


.. literalinclude:: ../json/campaign-sugartrap.json
   :language: json
