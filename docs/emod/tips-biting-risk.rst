=========================
Heterogeneous biting risk
=========================

This page provides an overview of how and when to use the |EMOD_s| features for heterogeneous
biting risk.


.. contents:: Contents
   :local:


What is heterogeneous biting risk and why would you want to include it?
=======================================================================

Many studies have identified substantial variance in the number of bites that individuals within a
population experience, which may be attributable to a combination of factors, such as individuals’
age, physiology, behavior, and location (`Irvine et al 2018 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5805933/>`__,
`Cooper et al 2019 <https://www.nature.com/articles/s41467-019-11861-y>`__). Including biting
risk heterogeneity in malaria transmission models is important for accurately capturing prevalence,
incidence, probability of elimination, and other important simulation outcomes. To capture this
heterogeneity in |EMOD_s|, we specify both age-specific risks and individual relative risks, which
can increase or decrease the number of bites an individual tends to experience relative to the mean
risk in the population.


Changing the distribution of relative biting risks does not change the total number of bites given
to the population, but it does change how those bites are distributed among individuals. People with
higher risk have a higher probability of receiving bites than people with lower risk. Because it is
a relative biting rate, the exact values assigned do not matter, only their relation to the sum of
all risks in the population. For example, giving everyone a value of 10 is the same as giving
everyone a value of 1.

A brief description of the different ways of specifying heterogeneous biting in |EMOD_s| is given
below, along with links to the main documentation pages for each type.


Age_Dependent_Biting_Risk_Type
==============================

Where is it specified?
----------------------

The relative biting risk among people of different ages is specified in the configuration file with
the **Age_Dependent_Biting_Risk_Type** parameter. There are three options for the type of distribution
used (‘OFF’, ‘LINEAR’, or ‘SURFACE_AREA_DEPENDENT’, which are explained in :doc:`parameter-configuration-infectivity`.

Who does it apply to?
---------------------

If Age_Dependent_Biting_Risk_Type is enabled, the biting risk of everyone in the population is
modified according to their age. This includes people who were created at the beginning of the
simulation as well as people who are born during the simulation.

How does serialization affect it?
---------------------------------

Yes, one can change this parameter when reading from a serialized file.  The age dependent part of
an individual’s biting risk is calculated each time step.

.. If the simulation was a pickup from a serialized file that didn’t have age-specific biting risks,
.. is this parameter from the serialization config overwritten?? And vice versa?

When should it be used?
-----------------------

If you aim to capture more realistic relative biting risks across ages in your simulation, it is
generally a good idea to enable age-dependent biting risk.



Biting risk demographics
========================

Where is it specified?
----------------------

The distribution of relative biting risks across the entire population is specified in the
demographics file under **IndividualAttributes** using the **RiskDistributionFlag** (which provides the type of distribution used)
along with **RiskDistribution1** and **RiskDistribution2** parameters (which specify the shape of the
distribution). Details on the values for these parameters can be found in :doc:`parameter-demographics`.

.. note::

    It is necessary to also set **Enable_Demographics_Risk** to 1 in the configuration file,
    otherwise the demographics risks will be ignored in the simulation.


Who does it apply to?
---------------------

When the relative biting risk distribution is set in the demographics file, all individuals that are
created at initialization and all individuals that are born during the simulation have relative
biting risks that are drawn from that distribution.


How does serialization affect it?
---------------------------------

An individual that is deserialized from the file will have whatever relative biting risk they had
when they were deserialized.  However, if **Enable_Demographics_Risk** were serialized on, then
newborns will get new relative biting risk values based on the
**RiskDistributionFlag**, **RiskDistribution1**, and **RiskDistribution2** parameters in the demographics file.

Individual’s risks do not change at serialization.

..  (What happens if a new demographics file is used for the pick-up? Are new individuals created with whatever the new demographics file specifies as the biting risk distribution?)


When should it be used?
-----------------------

The demographics approach for specifying relative biting risk is well-suited for simulations where
you want to include a more realistic distribution of risks across all individuals in the population.



Biting risk intervention
========================

Where is it specified?
----------------------

The biting risk intervention campaign is a campaign that changes the biting risk of a specified
group of people at a particular point in time in the simulation. Details on setting up biting risk
intervention campaigns can be found in :doc:`parameter-campaign-individual-bitingrisk`.


Who does it apply to?
---------------------

Like other intervention campaigns, individuals with certain individual properties, ages, etc. can be
targeted, or it can be distributed to the entire population. Only people who exist in the simulation
at the time the campaign occurs are affected. This contrasts with the demographics approach to
setting the risk distribution, where all individuals are initialized or born with risks drawn from
the distribution.


Will an individual's current risk be overwritten?
-------------------------------------------------

Implementing a biting risk intervention campaign overwrites the existing relative biting risk values
of targeted individuals (regardless of these biting risks were set using the demographics file or a
previous biting risk intervention). The new biting risk values that are assigned are independent of
the biting risk a person had previously.


How does serialization affect it?
---------------------------------

Individual’s risks do not change at serialization. However, whenever there is a new **BitingRisk**
intervention, it will overwrite existing relative risk values.


When should it be used?
-----------------------

The intervention version of setting biting risks is best suited for situations where you want a
subset of the population to have a different risk than everyone else. For example, if you want a
group of people who work in high-risk areas to have substantially higher risk than the general
population, you can use IPs and biting risk campaigns to target those individuals.


Common questions
================

#. What are reasonable parameters to use for the relative biting risk?
    Check out these blog posts comparing different parameterizations with data, found
    `here <https://paper.dropbox.com/doc/MSYNC-2021-02-03-Heterogeneous-biting--BVONsYCwLtgcv9Z~CAkkEwiIAg-TWWnHaOM2OXSaMziu1m0l>`__,  and `here <https://paper.dropbox.com/doc/2018-07-30-Setting-heterogeneous-biting-risk-parameters--BVOMld8eT9JNrkgkYn~cwu6vAg-L78dwE4aWiVzMSbHwZxeW>`__.

    Note that you must have permission to this private folder to view the blog posts.

#. Do heterogeneous biting risks apply when the model is configured to use forced EIR instead of mechanistic mosquito bites?
    No, but there are different parameters that can be used to specify age-based heterogeneity.
