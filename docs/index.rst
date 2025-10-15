===========================================
|EMOD_s| and |EMODPY_malaria| documentation
===========================================

This documentation set describes how to use |EMOD_l| for simulating malaria transmission
and interventions and how to use |EMODPY_malaria| for creating input files, submitting 
simulation jobs to a compute cluster, and more.


.. contents:: Contents
   :local:

|EMOD_l|
==========

The |IDM_l| develops disease modeling software that is thoroughly tested and shared with the
research community to advance the understanding of disease dynamics. This software helps determine
the combination of health policies and intervention strategies that can lead to disease eradication.
If you encounter any issues while using the software, please contact idm@gatesfoundation.org.

|EMOD_s|, is an :term:`agent-based model` (ABM) that simulates the
simultaneous interactions of agents in an effort to recreate complex phenomena.  Each agent (such as
a human or vector) can be assigned a variety of "properties" (for example, age, gender, etc.), and
their behavior and interactions with one another are determined by using decision rules. These
models have strong predictive power and are able to leverage spatial and temporal dynamics.

|EMOD_s| is also :term:`stochastic`, meaning that there is randomness built into the model. Infection
and recovery processes are represented as probabilistic Bernoulli random draws. In other words, when
a susceptible person comes into contact with a pathogen, they are not guaranteed to become infected.
Instead, you can imagine flipping a coin that has a λ chance of coming up tails S(t) times, and for
every person who gets a "head" you say they are infected. This randomness better approximates what
happens in reality. It also means that you must run many simulations to determine the probability of particular outcomes. 

The |EMOD_s| documentation is broken up into disease-specific sets that provide
guidance for researchers modeling particular diseases. The documentation contains only the
parameters, output reports, and other components of the model that are available to use for malaria modeling.

|EMODPY_malaria|
================

|EMODPY_malaria| is a collection of Python scripts and utilities created to
streamline user interactions with |EMOD_s| and |IT_s| for modeling malaria.
Much of the functionality is inherited from `emod-api <https://docs.idmod.org/projects/emod-api/en/latest/>`__ and :doc:`emodpy:emodpy`.

Additional information about how to use |IT_s| can be found in
:doc:`idmtools:index`.  Additional information about |EMOD_s| malaria
parameters can be found in :doc:`emod/parameter-overview`.

See :doc:`idmtools:index` for a diagram showing how |IT_s| and each of the
related packages are used in an end-to-end workflow using |EMOD_s| as the
disease transmission model.


.. toctree::
   :maxdepth: 3
   :titlesonly:

   installation
   overview
   emod/tutorials
   reference
   faq
   glossary


.. toctree::
   :maxdepth: 3
   :titlesonly:
   :caption: Related documentation

   emod-api <https://docs.idmod.org/projects/emod-api/en/latest/>
   emodpy <https://docs.idmod.org/projects/emodpy/en/latest/>
   idmtools <https://docs.idmod.org/projects/idmtools/en/latest/>
   idmtools-calibra <https://docs.idmod.org/projects/idmtools_calibra/en/latest/>