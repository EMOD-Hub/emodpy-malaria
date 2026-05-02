===============
MosquitoRelease
===============

The **MosquitoRelease** intervention class adds mosquito release vector control programs to the simulation.
Mosquito release is a key vector control mechanism that allows the release of sterile males,
genetically modified mosquitoes, or even Wolbachia- or Microsporidia-infected mosquitoes.
See :doc:`parameter-configuration-vector-control` configuration parameters for more information.

Released vectors are added to the population and participate in the vector life cycle and mating system the same day.

You can also release already-mated females to guarantee specific genomes in the offspring by setting the **Released_Mate_Genome** parameter.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-mosquitorelease.csv

.. literalinclude:: ../json/campaign-mosquitorelease.json
   :language: json