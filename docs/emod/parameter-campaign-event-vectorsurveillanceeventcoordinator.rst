==================================
VectorSurveillanceEventCoordinator
==================================

The **VectorSurveillanceEventCoordinator** coordinator class samples the vector population
at regular intervals and reports allele frequencies or genome fractions. It is configured with
a **Counter** object that specifies the species, gender, sample size, and counting method, and
a **Responder** object that can broadcast an event each time a survey is completed. Sampling
is controlled by trigger events: the coordinator begins sampling when an event from
**Start_Trigger_Condition_List** is received, and stops when an event from
**Stop_Trigger_Condition_List** is received or the **Duration** expires.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-vectorsurveillanceeventcoordinator.csv

.. literalinclude:: ../json/campaign-vectorsurveillanceeventcoordinator.json
   :language: json
