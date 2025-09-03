========
InputEIR
========

The **InputEIR** intervention class enables the Entomological Inoculation Rate (EIR) to be
configured either for each month or for each day of the year in a particular node. The EIR is the number of
infectious mosquito bites received in a night. This number is usually calculated by taking the number of mosquito
bites received  per night and multiplying them by the proportion of those bites that are positive for sporozoites.

This intervention class can be used instead of including vectors in the model as it will distribute
infections to people, somewhat mimicking vector biting. An individual's probability of receiving an
infection will be affected by is affected by **Age_Dependent_Biting_Risk_Type** and related parameters' settings,
**Enable_Demographics_Risk** and related parameters' settings, and any **AcquisitionBlocking** vaccines that
an individual may have received. Vector control interventions will not affect the EIR delivered by this intervention.

If vectors are  included when this class is implemented, this will add the EIR specified for that month or day in
addition to the EIR provided by the vectors. Note that the **Daily EIR channel** in the :doc:`software-report-inset-chart`
will not be impacted by this intervention.

When distributing **InputEIR** to a node that already has an existing **InputEIR** intervention, the existing
intervention will be purged and replaced with the new intervention.

**Note**: **Age_Dependence** parameter has been removed from this intervention. Age dependent biting risk is now
controlled by the **Age_Dependent_Biting_Risk_Type parameter** in the config file, the same as for vector biting.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-inputeir.csv

.. literalinclude:: ../json/campaign-inputeir.json
   :language: json
