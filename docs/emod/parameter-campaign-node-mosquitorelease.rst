===============
MosquitoRelease
===============

The **MosquitoRelease** intervention class adds mosquito release vector control programs to the simulation.
Mosquito release is a key vector control mechanism that allows the release of sterile males,
genetically modified mosquitoes, or even Wolbachia-infected mosquitoes. See :doc:`parameter-configuration-vector-control`
configuration parameters for more information.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-mosquitorelease.csv

.. literalinclude:: ../json/campaign-mosquitorelease.json
   :language: json