===============
MosquitoRelease
===============

The **MosquitoRelease** intervention class adds mosquito release vector control programs to the simulation.
Mosquito release is a key vector control mechanism that allows the release of sterile males,
genetically modified mosquitoes, or even Wolbachia-infected mosquitoes. See :doc:`parameter-configuration-vector-control`
configuration parameters for more information.

Released female vectors are added to the immature queue fully progressed, causing them to
emerge and mate on the first time step after release. Released male vectors are also added to the
immature queue so they emerge at the same time as the females. At initialization (as opposed to
campaign release), male vectors are added directly to the male queue so they are immediately
available for mating.

You can also release already-mated females to guarantee specific genomes in the offspring by setting the **Released_Mate_Genome** parameter.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-mosquitorelease.csv

.. literalinclude:: ../json/campaign-mosquitorelease.json
   :language: json