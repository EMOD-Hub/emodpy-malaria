============
SimpleBednet
============

The **SimpleBednet** intervention class implements :term:`insecticide-treated nets (ITN)` in the
simulation. ITNs are a key component of modern malaria control efforts, and have recently been
scaled up towards universal coverage in sub-Saharan Africa. Modern bednets are made of a
polyethylene or polyester mesh, which is impregnated with a slowly releasing pyrethroid insecticide.
When mosquitoes that are seeking a blood meal encounter a net,  the feeding attempt is blocked as
long as the net retains its physical integrity and has been correctly installed. Blocked feeding
attempts also carry the possibility of killing the mosquito. Net ownership is configured through the
demographic coverage, and the blocking and killing rates of mosquitoes are time-dependent.

**SimpleBednet** can model the bednet usage of net owners by reducing the daily efficacy. To model
individuals using nets intermittently, see :doc:`parameter-campaign-individual-usagedependentbednet`.
To include multiple insecticides, see :doc:`parameter-campaign-individual-multiinsecticideusagedependentbednet`.


At a glance:

*  **Distributed to:** Individuals
*  **Serialized:** Yes, if it has been distributed to a person.
*  **Uses insecticides:** Yes. Insecticides can be used to target specific species or other subgroups.
*  **Time-based expiration:** No, but it will expire if the WaningEffect expires (WaningEffectRandomBox and WaningEffectMapLinear expire).
*  **Purge existing:** Yes. If a new intervention is added to to the individual, the existing intervention with the same Intervention_Name is removed. It is possible to have multiple **SimpleBednet** interventions attached to an individual if they have different **Intervention_Name** values.
*  **Vector killing contributes to:** Indoor Before/After Feeding
*  **Vector effects:** Repelling, blocking, killing
*  **Vector sexes affected:** Females only
*  **Vector life stage affected:** Adult


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-simplebednet.csv

.. literalinclude:: ../json/campaign-simplebednet.json
   :language: json