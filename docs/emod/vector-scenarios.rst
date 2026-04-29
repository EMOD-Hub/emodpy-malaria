=======================
Vector model scenarios
=======================


The |EMOD_s| vector model is explained in detail in :doc:`vector-model-overview`. While the various
components that comprise the model are explained with examples, it may be more useful to learn the
model through hands-on implementation. The following sections introduce sets of example files
that illustrate how the vector model works on particular topics.

For more information on the software architecture and inheritance, see :doc:`software-overview`.

.. contents:: Contents
   :local:


The scenarios included for learning the vector model can be broken down into two categories:
"baseline simulation scenarios," which focus on the :term:`configuration file`, and "scenarios with
campaigns," which introduce the use of a :term:`campaign file`. All scenarios utilize vector-based
transmission. Note that climate is an important aspect of vector-based transmission, so every
scenario will utilize climate files in addition to demographic files.


Baseline simulation scenarios
=============================

These scenarios introduce users to the basic structure of the model, including how climate is
important in vector-based transmission models. There are no campaign interventions included for the
baseline scenarios.


Simple vector model
-------------------

This scenario introduces users to the VECTOR_SIM, which utilizes vector-based disease transmission.
In this simulation type, parameters for multiple vector species can be configured. The purpose of
this scenario is to familiarize users with the vector model, and to introduce parameters that are
species-specific to the included vectors. The scenario includes three species of mosquitoes, but
does not include any campaign interventions.


Impact of climate on seasonality
--------------------------------

While climate is used in every vector simulation type, this scenario explores how
differences in climate impact vector-borne disease transmission. The simulation utilizes the VECTOR_SIM to show
how transmission is impacted differentially in three locations that vary in their climate. The
base configuration is the same for the different locales, yet vector populations will vary
drastically due to temperature, humidity, and rainfall. The purpose of this scenario is to help
familiarize the user with the importance of accurate climate files, as they have a large impact
on the seasonality of disease transmission.



Scenarios with campaigns
========================

The baseline scenarios are meant to familiarize the user with basic model functionality and setup.
The scenarios in this section build upon the concepts previously demonstrated, and add in the use
of campaign interventions. Each scenario below includes a campaign file, and each will demonstrate
the functionality of various interventions.



Bednet distribution
-------------------

Bednets are commonly used to protect individuals from vector-borne diseases; in this scenario,
:term:`insecticide-treated nets (ITN)` are introduced as an intervention. These nets, also known as
bednets, are a commonly used and effective strategy to prevent disease transmission. The purpose
of this scenario is twofold: first, the use of campaign files is introduced, and second, the
use of bednets as an intervention is demonstrated.



Bednets and acquisition-blocking vaccines
-----------------------------------------

This scenario builds upon the "Bednet distribution" scenario by combining multiple interventions.
The same configuration file is used, and bednets are included; in addition to the bednets, an
acquisition-blocking vaccine is included in the campaign file. The purpose of this scenario is to
familiarize users with campaign files that utilize multiple strategies. Eradication programs
typically rely on combinations of interventions, not a single intervention in isolation. Therefore,
it is important for modelers to be familiar with creating such complex strategies.



Multiple interventions: Bednets, IRS, acquisition- and transmission-blocking vaccines
-------------------------------------------------------------------------------------

This scenario builds upon the concept of complex strategies that was introduced in the "Bednets
and acquisition-blocking vaccines" scenario by using a combination of four interventions. The
campaign file includes the bednets and acquisition-blocking vaccines that were previously
introduced, and adds in :term:`indoor residual spraying (IRS)` and transmission-blocking vaccines.
The purpose of this scenario is to both introduce a different type of vaccine, and to demonstrate
that campaign files can be layered with numerous interventions to help recreate specific situations.


Sugar-baited traps
------------------

Previous scenarios utilized individual-level interventions. This scenario introduces a
:term:`node-targeted intervention`. These sugar-baited traps are applied at the :term:`node`
instead of distributed to individuals, and are used to collect host-seeking mosquitoes. The
purpose of this scenario is to familiarize the user with node-level interventions (here,
sugar traps). An interesting aspect of this intervention is that the efficacy can be modified
by mosquito feeding behavior and how frequently they seek sugar meals. This behavior can be
configured in the :term:`configuration file`.


Insect-killing fence
--------------------

As with the "Sugar-baited traps" scenario, this scenario utilizes a :term:`node-targeted intervention`,
insect-killing fences. There are several types of fences, such as photonic fences that kill
mosquitoes using lasers.  These fences can work to kill mosquitoes outdoors when they are either
on their way into a house to seek a blood meal, or on their way out of the house to oviposit. The
purpose of this scenario is to familiarize the user with node-level interventions (here,
insect-killing fences).


Linear combination vector habitat
---------------------------------

This scenario provides more detail on how to realistically configure larval habitat for mosquitoes.
Previous scenarios utilized single habitat types for the mosquitoes in the model; here, multiple
habitat types can be configured for each species. As mosquito species will typically have a
predominant habitat type, but opportunistically utilize other available habitat types, this is
an especially important feature of the model. The purpose of this scenario is to illustrate how
to configure multiple habitat types for a single vector species.





.. will want to include some vector genetics tutorials!