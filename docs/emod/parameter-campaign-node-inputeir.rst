========
InputEIR
========

The **InputEIR** intervention class enables the Entomological Inoculation Rate (EIR) to be
configured either for each month or for each day of the year in a particular node. The EIR is the number of
infectious mosquito bites received in a night. This number is usually calculated by taking the number of mosquito
bites received  per night and multiplying them by the proportion of those bites that are positive for sporozoites.

The probability of an individual becoming infected from the each 'infectious bite' will be affected by
**Age_Dependent_Biting_Risk_Type** and **Enable_Demographics_Risk** settings, as well as any
**AcquisitionBlocking** vaccines that an individual may have received.

Vector control interventions will not affect the EIR delivered by this intervention.

If vectors are  included when this class is implemented, this will add the EIR specified for that month or day in
addition to the EIR provided by the vectors. Note that the **Daily EIR channel** in the :doc:`software-report-inset-chart`
will not be impacted by this intervention.

When distributing **InputEIR** to a node that already has an existing **InputEIR** intervention, the existing
intervention will be purged and replaced with the new intervention.

**Note**: **Age_Dependence** parameter has been removed from this intervention (EMOD v2.28, emod-malaria v0.77).
Age dependent biting risk is now controlled by the **Age_Dependent_Biting_Risk_Type parameter** in the config file,
 same as for vector biting.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-inputeir.csv

.. literalinclude:: ../json/campaign-inputeir.json
   :language: json
