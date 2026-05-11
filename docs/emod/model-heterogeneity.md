# Adding heterogeneity


One of the benefits of an agent-based model like EMOD over compartmental models is that the the
model can be configured to capture heterogeneity in population demographics, migration patterns,
disease transmissibility, climate, interventions, and more. This heterogeneity can affect the
overall course of the disease outbreak and campaign interventions aimed at controlling it.


## Demographics


Built-in demographics options are available for running EMOD simulations, or you can create
customized demographics files to represent particular locations. It is generally 
recommended that you create a demographics file instead of using built-in demographics. 

Every individual within the simulation has a variety of attributes, represented by continuous or
discrete state variables. Some are static throughout life, and others dynamically change
through the course of the simulation, through response either to aging or to simulation events (such
as infection). Static attributes are assigned upon instantiation (simulation initialization or birth
after the beginning of the simulation) and include gender, time of birth, time of non-disease death, etc. Dynamic attributes include disease state, history of interventions, and more. 

## Vital dynamics


Vital dynamics within EMOD are derived from fertility and mortality tables that
are passed to the model as input. Input demographic data can be used to construct a cumulative
probability distribution function (CDF) of death date based on individuals' birth dates. Then, in
the model, individual agents will be sampled stochastically from this CDF using an inverse transform
of this distribution. Female agents similarly sample the age at next childbirth, if any, upon
instantiation and birth of a previous child. Pregnancy is not linked to relationship status,
although newly born individuals are linked to a mother. The fertility rate changes by simulation
year and female age, and the range for available estimates depends on input data. Values outside of
this range can be chosen by "clamping," or choosing the nearest value within the range. Clamping was
also used when necessary to determine the non-disease mortality rate, which varies by gender, age, and
simulation year.

For more information on the demographics file, see [Demographics file](software-demographics.md).

## Individual and node properties


One of the most powerful and flexible features of EMOD is the ability to assign properties to
nodes or individuals that can then be used to target interventions or move individuals through a
health care system. For example, you might assign various degrees of risk, socioeconomic status,
intervention status, and more. In the generic, environmental, typhoid, airborne, and TBHIV simulation types, these
properties can be leveraged to add heterogeneity in transmission based on the property values
assigned to each individual. For example, you might configure higher transmission among school-age
children. 

## Transmission


In EMOD, transmission can only happen within a geographic node, and the population is "well-mixed" in each node. Heterogeneous transmission is modeled through biologically
mechanistic parameters that control aspects of the simulation such as parasite density, symptom
severity, mosquito bites, and more. 

See [Infectivity configuration](parameter-configuration-infectivity.md) parameters for more information on configuring transmission in
this simulation type. Because HINT cannot be used with this simulation type, the parameter
**Enable_Heterogeneous_Intranode_Transmission** in the configuration file must be set to 0
(zero).

## Migration


EMOD can also simulate human and vector migration, which can be important in the transmission of
many diseases. You can assign different characteristics to each geographic *node* to control
how the disease spreads.

For more information on how you can target campaign interventions to individuals or locations based
on certain criteria, see [model-campaign](model-campaign.md).

