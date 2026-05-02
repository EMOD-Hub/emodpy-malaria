===========================================
|EMOD_s| and |EMODPY_malaria| documentation
===========================================

This documentation set describes how to use |EMOD_l| for simulating malaria transmission
and interventions and how to use |EMODPY_malaria| for creating model configuration files,
submitting simulation jobs to a compute cluster, and more.


.. contents:: Contents
   :local:

|EMOD_l|
==========

|EMOD_s| is a stochastic, :term:`agent-based model` developed by the |IDM_l| that simulates
the spread of infectious diseases. It models individual humans and mosquitoes and their
interactions, making it well-suited for evaluating malaria control strategies across a wide
range of transmission settings. See :doc:`emod/malaria-overview` for a full description
of the model.

If you encounter any issues while using the software, please visit our
`discussion board <https://github.com/orgs/EMOD-Hub/discussions>`__.


|EMODPY_malaria|
================

|EMODPY_malaria| is the primary interface for working with |EMOD_s|. It provides the
tools to configure the model, define interventions, set up simulation runs, and analyze
results — everything a researcher needs to go from a scientific question to a completed
simulation.


.. toctree::
   :maxdepth: 3
   :titlesonly:

   installation
   overview
   reference
   glossary


.. toctree::
   :maxdepth: 3
   :titlesonly:
   :caption: Related documentation

   emod-api <https://emod-hub.github.io/emod-api/>
   emodpy <https://emod-hub.github.io/emodpy/>
   idmtools <https://docs.idmod.org/projects/idmtools/en/latest/>
   idmtools-calibra <https://docs.idmod.org/projects/idmtools_calibra/en/latest/>