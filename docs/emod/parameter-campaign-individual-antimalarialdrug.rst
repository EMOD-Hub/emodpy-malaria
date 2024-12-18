================
AntimalarialDrug
================

The **AntimalarialDrug** intervention is used to apply drug-based control efforts to malaria
simulations. When configuring this intervention, note that the configuration parameter
**Malaria_Drug_Params** must be configured, as it governs how particular anti-malarial drugs will
behave.


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-antimalarialdrug.csv

.. literalinclude:: ../json/campaign-antimalarialdrug.json
   :language: json
