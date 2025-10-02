========
InputEIR
========

The **InputEIR** intervention class enables the Entomological Inoculation Rate (EIR) to be
configured for each month of the year in a particular node. The EIR is the number of infectious
mosquito bites received in a night. This number can be calculated by taking the number of mosquito
bites received  per night and multiplying them by the proportion of those bites that are positive
for sporozoites.

This intervention class can be used instead of including vectors in the model, as it will distribute
infections to people (it does not model vector biting). However, if vectors are  included when this
class is implemented, it will add the EIR specified for that month in addition to the EIR provided
by the vectors. Note that the Daily EIR channel in the :doc:`software-report-inset-chart` will not
be impacted by this intervention. When distributing **InputEIR** to a node that already has an existing
**InputEIR** intervention, the existing intervention will be replaced with the new one.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Does Not Apply
*  **Time-based expiration:** No.
*  **Purge existing:** Yes. Adding a new intervention of this class will overwrite an existing intervention of the same class.
*  **Vector killing contributes to:** Does Not Apply
*  **Vector effects:** Does Not Apply
*  **Vector sexes affected:** Does Not Apply
*  **Vector life stage affected:** Does Not Apply

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-inputeir.csv

.. literalinclude:: ../json/campaign-inputeir.json
   :language: json
