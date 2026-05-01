================
BirthTriggeredIV
================

Note: This intervention has been replaced by NodeLevelHealthTriggeredIV, which provides more flexibility and can be
triggered by any individual event, including **Births** which mimics the BirthTriggeredIV. BirthTriggeredIV will
continue to be supported for backward compatibility but will not receive new features.

The **BirthTriggeredIV** intervention class listens for births in a node and distributes
an individual-level intervention to each newborn. It is a node-level intervention that persists
on the node for the specified **Duration** (or indefinitely if set to -1), distributing the
configured **Actual_IndividualIntervention_Config** to qualifying newborns based on demographic
targeting and property restrictions.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-birthtriggerediv.csv

.. literalinclude:: ../json/campaign-birthtriggerediv.json
   :language: json
