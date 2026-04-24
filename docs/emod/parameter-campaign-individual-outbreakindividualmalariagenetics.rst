=================================
OutbreakIndividualMalariaGenetics
=================================

The **OutbreakIndividualMalariaGenetics** intervention class is an individual-level intervention
that extends the :doc:`parameter-campaign-individual-outbreakindividual` class by adding the ability
to specify parasite genetics for the infection. This class is only used when the configuration
parameter **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

.. seealso::

   :doc:`malaria-model-fpg`
      For the full FPG workflow, including genome configuration, seeding modes, recombination, and output reports.

The parameter **Create_Nucleotide_Sequence_From** (see table below) determines how the parasite
genetics are defined.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-outbreakindividualmalariagenetics.csv

.. literalinclude:: ../json/campaign-outbreakindividualmalariagenetics-barcode.json
    :language: json

.. literalinclude:: ../json/campaign-outbreakindividualmalariagenetics-allele.json
    :language: json

.. literalinclude:: ../json/campaign-outbreakindividualmalariagenetics-nucleotide.json
    :language: json
