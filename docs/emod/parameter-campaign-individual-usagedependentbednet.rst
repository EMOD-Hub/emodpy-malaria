====================
UsageDependentBednet
====================

The **UsageDependentBednet** intervention class is similar to :doc:`parameter-campaign-individual-simplebednet`,
as it distributes insecticide-treated nets to individuals in the simulation. However,
bednet ownership and bednet usage are distinct in this intervention. As in **SimpleBednet**, net
ownership is configured through the demographic coverage, and the repelling, blocking, and killing rates of
mosquitoes are time-dependent. Use of bednets is age-dependent and can vary seasonally. Once a net
has been distributed to someone, the net usage is determined by the product of the seasonal and
age-dependent usage probabilities until the net-retention counter runs out, and the net is discarded.

While **SimpleBednet** usage is applied as a daily reduction in efficacy, **UsageDependentBednet**
uses the usage efficacy to determine whether or not the person used the net that day.  For example,
if we look at bednet with 0% repelling, 100% blocking, and 100% killing effects, and 50% usage effect,
the person with the **SimpleBednet** will have a net that has final efficacy of 50% blocking and 50% killing
each day and the person with the **UsageDependentBednet** will have half of their days with a 100% blocking and
100% killing net and half of their days with no net at all. Note that when a person migrates, they
take their net with them.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if this has already been distributed to a person.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes, especially if you want to target specific species.
*  **Time-based expiration:** Yes, an expiration timer that is independent from the waning effects can be configured.
*  **Purge existing:** Yes. Adding a new bednet intervention of any type will replace any other bednet interventions in an individual. The Intervention_Name parameter does not change this behavior.
*  **Vector killing contributes to:** Indoor Die Before Feeding
*  **Vector effects:** Repelling, blocking, and killing
*  **Vector sexes affected:** Indoor meal-seeking females only.
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-usagedependentbednet.csv

.. literalinclude:: ../json/campaign-usagedependentbednet.json
   :language: json