============================
Infectivity and transmission
============================

.. include:: ../reuse/config-infectivity.txt

The malaria transmission model does not use many of the parameters provided by the generic simulation
type. Instead, :term:`gametocyte` abundances and :term:`cytokine` mediated infectiousness are
modeled explicitly. See :doc:`vector-model-transmission` for more information.

.. seealso::

   :doc:`malaria-model-fpg`
      For ``Max_Individual_Infections`` and other transmission parameters as used in FPG simulations.


.. include:: ../reuse/warning-case.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/config-infectivity-malaria.csv
