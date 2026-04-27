=======================
Malaria model scenarios
=======================


The |EMOD_s| malaria model is explained in detail in :doc:`malaria-model-overview` and the
vector model it is built upon is described in :doc:`vector-model-overview`. While the
various components that comprise the model are explained with examples, it may be more useful to
learn the model through hands-on implementation. The following sections introduce sets of
example files that illustrate how the malaria model works on particular topics.


For more information on the software architecture and inheritance, see :doc:`software-overview`.

Full malaria model
==================

This scenario introduces users to the MALARIA_SIM, which builds upon the vector-transmission of the
VECTOR_SIM and adds malaria-specific parameters. Specifically, users can configure malaria drug
parameters, and disease parameters are specific to malaria (instead of having a more generic form).
The purpose of this scenario is to introduce the user to the model features that are unique to the
malaria model, and to demonstrate how they contribute to facilitate understanding of malaria
epidemiology.




Garki project retrospective: IRS and MDA
========================================

This scenario uses a historical data set from the `The Garki Project <https://apps.who.int/iris/handle/10665/40316>`__
to examine how :term:`indoor residual spraying (IRS)` and :term:`mass drug administration (MDA)`
impact malaria transmission. Previous scenarios introduced IRS, but utilized vaccination campaigns
instead of MDA.  To use MDA, the simulation type will be the MALARIA_SIM, and the configuration
file will contain parameters to set the efficacy of specific drugs. As with generic vaccinations,
the campaign file will then be used to distribute the vaccines to the desired portion of the
population. The purpose of this scenario is twofold: first, it will allow the user to explore
the Garki dataset, and second, it will introduce a new intervention (MDA).

