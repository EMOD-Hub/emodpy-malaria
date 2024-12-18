================================
Malaria symptoms and diagnostics
================================

In |EMOD_s|, parameters for multiple types of malaria symptoms are included. Symptoms indicate the
presence of disease, and one of the most prevalent types of data used to inform models is case data.
By leveraging such data, models can help elucidate the processes that cause disease and enable
calculations of the likely percent of the population that is infected (or infectious). Similarly,
in order to model treatment-seeking behaviors (which will change the transmission dynamics of malaria),
it is necessary to have a spectrum of disease severity (and hence, a spectrum of symptom parameters).
Finally, disease severity is related to past infection and immune response, so inclusion of symptoms
can help to further inform transmission dynamics of the target population.


For a complete list of configuration parameters that are used in the malaria model, see the
:doc:`parameter-configuration`.


Fever and clinical cases
========================

Fever is triggered by :term:`cytokine` production through the innate immune response. A clinical case begins
when fever surpasses a certain threshold and the clinical incident continues until fever subsides
below another threshold.

.. figure:: ../images/vector-malaria/Malaria_Symptoms_fever_and_clinical_cases.png

   Fever and clinical case definition



Anemia
======

Rupture of infected red blood cells (RBCs) destroys nearby RBCs and leads to anemia. Erythropoiesis is
stimulated in anemic individuals to increase the rate of RBC production.

.. figure:: ../images/vector-malaria/Malaria_Symptoms_anemia.png

   Anemia

.. _malaria-severe-mortality:

Severe disease and mortality
============================

Excessive fever, anemia, or parasite counts can all lead to severe disease and mortality.

.. figure:: ../images/vector-malaria/Malaria_Symptoms_severe_disease_and_mortality.png

   Severe disease and mortality



Diagnostics
===========

Malaria diagnostics test for the presence of asexual parasites in an individual’s blood. A parasite
count is drawn from a Poisson distribution centered around the true asexual parasite count.

.. figure:: ../images/vector-malaria/Malaria_Symptoms_diagnostics.png

   Diagnostics



