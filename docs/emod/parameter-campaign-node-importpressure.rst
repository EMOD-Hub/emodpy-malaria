==============
ImportPressure
==============

The **ImportPressure** intervention class extends **Outbreak** by importing infected individuals
into a node at a configurable rate over specified time periods. Each element in the
**Daily_Import_Pressures** array is applied for the corresponding number of days in the
**Durations** array, allowing time-varying importation schedules. The imported cases are
created with the specified **Antigen**, **Genome**, and **Import_Age**.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-importpressure.csv

.. literalinclude:: ../json/campaign-importpressure.json
   :language: json
