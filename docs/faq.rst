===
FAQ
===

As you get started with |EMODPY_malaria| and |EMOD_s|, you may have questions. The most common
questions are answered below. The most common questions are answered below. 
For questions related to functionality in related packages, see the
following documentation:

* :doc:`idmtools:faq` for |IT_s|
* `FAQ <https://docs.idmod.org/projects/emod-api/en/latest/faq/>`__ for |emod_api|
* :doc:`emodpy:faq` for |EMODPY_s|

This section also includes topics on troubleshooting and some recommended tips and tricks
when working with |EMOD_s| and |EMODPY_malaria|.

.. contents:: Contents
   :local:

What are some of the key differences for people used to using dtk-tools?
========================================================================

1. Schema-Based. The creation of config and campaign files is entirely schema-based now. This means that you can only set parameters that the binary you are using recognizes. And parameter types and ranges are enforced at runtime.
2. Inter-File Dependencies Now Automatic. Before there were lots of parameters in the config that you had to set to correspond to settings in campaign or demographics files. That is no longer the case. We call these 'implicits'. For example, if you add a BirthRate to the demographics, the corresponding parameters in the config.json (Enable_Births) will get set automatically for you. As another example, when you create a campaign and specify various 'events' to be broadcast/published and/or listened/subscribed to, you no longer have to figure out which ones are built-in and which are ad-hoc. It does that for you and populates the Custom_Events param on your behalf.
3. Hierarchical Dependencies Now Automatic. If a parameter depends on another parameter, previously you had to set all the Enables in the dependency tree. Now they get set automatically for you. For example, if Enable_Birth is set (see above), Enable_Vital_Dynamics will be set for you.
4. No JSON manipulation. dtk-tools worked primarily through manipulation of JSON that made up the configuration files. You no longer need to have any knowledge of the internal representation of data in the DTK input files. All configuration should be done via Python functions.
5. Released and Installed Modules. We want users mostly using versioned released modules that have been pip installed, not git cloned, dev-installed code, except during development. The process of getting new code reviewed, tested, and getting the module versioned and released is intended to be smooth and efficient when everyone does their defined role. "Trust The Process and Do Your Job", as someone once said.
6. Blessed Binaries. In dtk-tools you would often BYOB -- Bring Your Own Binary -- but in emodpy, the idea is that the system pulls down the latest CI (Continuous Integration) build for your disease that passed all the tests. We very much want to noramlize the idea of doing research with versioned software that has come through our professional BVT processes.

Do I need to install a whole bunch of Python modules? Where do I get that list?
===============================================================================

No. You should only have to install emodpy-malaria, and everything else should come as a dependency automatically. If you are starting from a workflow repo, there should be a requirements.txt file that lists a particular version of emodpy-malaria. Then 'pip install -r requirements.txt' is what you should expect to do.

Is there an easier way than typing --index-url with that long URL every time I use pip?
=======================================================================================

Yes. You should not be typing that every time. You should update the pip.ini (Windows) or pip.conf globally on your computer with that URL and never have to type it again.

How do I find the path or file to my pip.ini?
=============================================
::

    pip config -v list. 
    
Choose the first or second one.

What if the pip.ini file (or pip folder) doesn't exist?  
===============================================================================

Go ahead and create it (at one of the locations specified by 'pip config -v list'). It's your computer.  

What's the text I need to enter into my pip config file?
========================================================
::

    [global]
    index-url = https://packages.idmod.org/api/pypi/pypi-production/simple

I was installing the Python modules and it told me I needed a C++ compiler?
===========================================================================

This is because of a dependency in some versions of emod-api on lz4. lz4 usually comes as what's called a source package and it has to be compiled as part of the install. This requires a compiler, which doesn't come by default on Windows computers. At this point, if your pip.ini is set up properly, you should be able to get a pre-built lz4 package from our local Artifactory PIP server.

I was installing and got prompted for JFrog credentials.
========================================================

You should not have to give credentials to use our JFrog/Artifactory/pip server. Credentials are required to get packages from the staging server. We don't expect end users to be accessing packages from staging, just prod, which is auth-free.

What if I really actually do want to install something from staging?
====================================================================

You need to specify '--index-url = https://<username>@idmod.org:<shh...password>@packages.idmod.org/api/pypi/pypi-staging/simple' and also provide your creds when prompted.

What version of Python should I be using?
=========================================

At least Python 3.7.7. If you are installing a new version of Python, feel free to go all the way forward to a Python 3.9.x. 3.8 is probably the sweet spot of "known to work and still not considered old".

What if I want a particular version of emodpy-malaria?
======================================================
::

    pip install emodpy-malaria==1.2.3

Should get you what you need.

What if I want to make changes to emodpy-malaria and run with those, instead of a released version?
===================================================================================================

(This is a duplicate.)

There are a couple of ways of doing that. 
Option 1: Do a Dev Install::

    pip install -e .

This will make your site packages map to your local code until you do a new pip install of the package.

Option 2: Creating a wheel from your local code and pip install it (each time you make a change).::

    python setup.py bdist_wheel
    pip3 install dist/<newly_create_file.whl>

Some people prefer option 1 because it's "one and done". Some people prefer option 2 because it keeps you thinking in terms of packaging, versioning, and installing even while you're developing.

I pip installed |EMODPY_malaria|, but I want to make changes. How should I do that?
===================================================================================

Install at a command prompt using the following::

    python setup.py develop

This method is the most popular and proven, though there are some other
options. Installing this way means that the |EMODPY_malaria| module in
site-packages actually points to the same code as you have checked out in git.
For more detail, see this `Stack Overflow post
<https://stackoverflow.com/questions/19048732/python-setup-py-develop-vs-install#19048754>`_.

However, we aim to get the desired changes quickly tested and included in the
versioned module we release via pip install.


How do I set configuration parameters?
======================================

Define your own parameter-setting function such as ``set_param_fn`` and pass
that function to the |EMODPY_s| task creator as the ``param_custom_cb``
parameter. In that function, you can set the parameters directly. For
example:

.. literalinclude:: ../examples/start_here/example.py
  :lines: 55-82

See examples/start_here/example.py. for additional information.

If you prefer something more modular, you can call a function in a standalone
script/file that sets the configuration parameters.

Are there defaults?
   Great question. If you don't set any configuration parameters, they will have
   defaults based on the schema. The malaria team has set team defaults in
   :py:meth:`emodpy_malaria.config.set_team_defaults`. These defaults can be seen
   in `config.py <https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/emodpy_malaria/config.py>`_.


How do I specify the log level for |EMOD_s|? I get a schema error when I try to set it now.
===========================================================================================

TBD

How do I specify the vector species for my scenario?
====================================================

See the excerpt below or the complete example of setting the vector species
and parameter values associated with each species in
examples/start_here/example.py.

.. literalinclude:: ../examples/start_here/example.py
  :lines: 55-82

A helper function to make this task even easier may be coming shortly.


Where else should I search for functions?
=========================================
Yes, `emod-api <https://docs.idmod.org/projects/emod-api/en/latest/>`_. Any functionality that is not malaria-specific (or disease-specific) will be found in emod-api. In particular you'll probably find very useful functions for crafting campaigns in `emod-api.interventions.common <https://docs.idmod.org/projects/emod-api/en/latest/emod_api.interventions.common.html>`_, such as the `ScheduledCampaignEvent <https://docs.idmod.org/projects/emod-api/en/latest/emod_api.interventions.common.html#emod_api.interventions.common.ScheduledCampaignEvent>`_ function and the `TriggeredCampaignEvent <https://docs.idmod.org/projects/emod-api/en/latest/emod_api.interventions.common.html#emod_api.interventions.common.TriggeredCampaignEvent>`_ function.


Do I need to be connected to the VPN?
=====================================
The original way of procuring the model binary itself was via a call to get_model_files(). This required you to be VPN-ed in. This is no longer the preferred approach. Instead you will want to use the 'bootstrap' approach. This involves installing the emod_malaria package, which should happen automatically, and using code like::

    import emod_malaria.bootstrap as dtk
    dtk.setup(...)

This does not require VPN. The value you pass to setup is the path where the model files will be put.


Is there an example of creating a demographics file from scratch with the API?
==============================================================================

Yes, see examples/create_demographics, there are also examples in emodpy-measles and emodpy-hiv.
We are working to add some to emod_api.demographics. The basic idea is you use one of 3 node creators,
and then use the Setter API to set up the node defaults for fertility, mortality, age structure, initial immunity,
individual 'risk', and initial prevalance.
The first node creator, from_template_node, is very basic and usually for
quickstarts or toy models. It lets you create a single node demographics file with a given population.
The second creator, from_csv, lets you create a multinode demographics using a csv file with population data as
an input.
The third creator, from_params, lets you create a multinode demographics without specific node data but instead with
a few parameters that represent the overall population and the population heterogeneity.


I see a lot of MALARIA_SIM examples. Are there any VECTOR_SIM examples?
=======================================================================

Yes! The following examples use VECTOR_SIM:

  * `migration_spatial_vector_sim <../examples/migration_spatial_vector_sim>`_
  * `vector_basic <../examples/vector_basic>`_
  * `vector_genetics_insecticide_resistance <../examples/vector_genetics_insecticide_resistance>`_
  * `vector_genetics_vector_sim <../examples/vector_genetics_vector_sim>`_

Is there a multi-node or spatial example?
=========================================

Yes. See:

  * examples/migration_spatial_vector_sim
  * examples/migration_spatial_malaria_sim
  * examples/jonr_1

Are there simple campaign/intervention examples?
================================================

Yes. See:

  * examples/outdoor_rest_kill_male_mosquitoes
  * examples/inputEIR
  * examples/ivermectin

Is there a drug campaign example? 
=================================

Yes. See:

  * examples/drug_campaign
  * examples/diagnostic_survey

Is there a campaign sweep example? 
==================================

Yes. See:

  * examples/campaign_sweep

Is there a demographics sweep example? 
======================================

Yes. See:

  * examples/demographics_sweep

Is there a serialization/burn-in example? 
=========================================

Yes. See:

  * examples/burnin_create
  * examples/burnin_use

Is there a reporter configuration example? 
==========================================

Yes. See:

  * examples/add_reports
  * examples/filtered_report

Why doesn't anything happen when I double-click |exe_s|?
========================================================

Unlike many executable files, |exe_s| does not open a software installer when double-clicked.
Instead, you must provide |exe_s| with various input files used to run a simulation and create
outputs. You can run simulations in a number of ways. The simplest way to learn about the model
is to run individual simulations at the command line. However, because |EMOD_s| is a stochastic
model, this is not feasible when you must run many simulations to create useful output for
statistical analysis. Once you advance to that stage, you will want to use other software tools
to run multiple simulations either locally or, more often, on an HPC cluster. For more
information, see :doc:`emod/install-overview` and :doc:`emod/software-run-simulation`.


Where do I get demographics and climate files? 
==============================================

|IDM_s| provides demographics and climate files for many different regions of the world in the
EMOD-InputData GitHub repository. See :doc:`emod/install-overview` for download instructions. If
there are no files available for the region you are interested in, contact idm@gatesfoundation.org

How do I plot my output? 
========================

|EMOD_s| does not produce plots of the data by default. Instead, it produces 
:term:`JSON (JavaScript Object Notation)` or CSV files that you can then parse and plot using
Python, MATLAB, R, or another programming language. The `EMOD scenarios`_ zip file contains input 
files and plotting scripts for many different disease modeling scenarios intended to teach 
|EMOD_s|. You may want to review these files to see examples of how the output can be plotted.

Does your model include X?
==========================

Many aspects of disease dynamics are explicitly modeled in |EMOD_s|. Review :doc:`emod/parameter-overview` 
for an exhaustive list of all parameters that can be used to enable functionality in
|EMOD_s|. If you want to model something that isn't listed there, |EMOD_s| provides highly
flexible functionality with the individual and node property feature. These properties label
individuals or regional nodes in a simulation so you can change disease outbreaks, transmission
dynamics, behavior, or treatment based on the assigned values. For example, you can add
properties to represent vitamin deficiencies, comorbidities, and more. For more information, see
:doc:`emod/model-properties`.

If individual and node properties cannot incorporate the functionality you need, |EMOD_s| is
open-source software that can be extended to meet your needs. For more information, see 
:doc:`emod:dev-install-overview`.

    
Can I model regions, countries, provinces, or cities? 
=====================================================

|EMOD_s| uses nodes to represent geographic areas. Each :term:`node` has a population and
associated characteristics. Individuals and, if relevant, vectors can migrate between nodes.
Nodes can represent areas of any scale you like, from entire countries to individual
households. 

Do you have a model for disease X?
==================================

The software architecture of |EMOD_s| has a "generic model" base upon which more specific
transmission modes and diseases are built. This allows common functionality to be shared for
modeling a variety of diseases. For example, the generic model can be used to model influenza,
measles, and more. You can also use one of the transmission mode simulation types (airborne,
STI, environmental, vector) to model diseases such as herpes, typhoid, dengue or others that we
don't explicitly support. Often, this can be done without the need to make any source code
changes.


.. _EMOD scenarios: https://github.com/InstituteforDiseaseModeling/docs-emod-scenarios/releases



.. toctree::
   :maxdepth: 3
   :titlesonly:

   emod/troubleshooting
   emod/tips-tricks
