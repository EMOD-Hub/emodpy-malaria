==================
Configuration file
==================

The primary means of configuring the disease simulation is the :term:`configuration file`. This
required file is a :term:`JSON (JavaScript Object Notation)` formatted file that is typically named
config.json. The configuration file controls many different aspects of the simulation. For example,

* The names of the :term:`campaign file` and other :term:`input files` to use
* How to use additional demographics, climate, and migration data (such as enabling features or scaling values)
* General disease attributes such as infectivity, immunity, mortality, and so on
* Attributes specific to the disease type being modeled, such as infectivity and mortality
* The reports to output from the simulation


Although you can create configuration files entirely from scratch, it is often easier to start from
an existing configuration file and modify it to meet your needs or use the provided Python packages
to create configuration files.


For a complete list of configuration parameters that are available to use with this simulation type,
see :doc:`parameter-configuration`. For more information about JSON, see :doc:`parameter-overview`.


Configuration files
=============================

A configuration file is a single-depth JSON file with configuration parameters
listed alphabetically. This is the configuration file format required by EMOD.

However, there may be some hierarchical elements in the flattened version. For example,
**Vector_Species_Params** and **Malaria_Drug_Params** have nested JSON objects.

Below is an example of a flattened configuration file:

.. literalinclude:: ../json/howto-generic-config-flat-full.json
   :language: json

