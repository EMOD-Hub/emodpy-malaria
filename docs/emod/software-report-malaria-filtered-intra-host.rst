================================
ReportMalariaFilteredIntraHost
================================

The malaria filtered intra-host report (ReportMalariaFilteredIntraHost.json) extends
:doc:`software-report-filtered-malaria` by replacing the standard InsetChart channels with a
focused set of within-host disease dynamics channels. It retains a small number of epidemiological
channels from the parent report and adds channels tracking infection stage distribution, cytokine
levels, MSP variant antibody fractions, and metrics on individuals carrying the maximum number of
simultaneous infections. Weather and vector channels are removed.


Configuration
=============

To generate this report, the following parameters must be configured in the custom_reports.json
file. All parameters are inherited from :doc:`software-report-filtered-malaria`.

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Filename_Suffix**, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
    **Start_Day**, float, 0, 3.40282e+38, 0, "The day of the simulation to start collecting data."
    **End_Day**, float, 0, 3.40282e+38, 3.40282e+38, "The day of the simulation to stop collecting data."
    **Node_IDs_Of_Interest**, array of integers, 0, 2.14748e+09, [], "Data will be collected for the nodes in this list. Empty list implies all nodes."
    **Min_Age_Years**, float, 0, 9.3228e+35, 0, "Minimum age in years of people to collect data on."
    **Max_Age_Years**, float, 0, 9.3228e+35, 9.3228e+35, "Maximum age in years of people to collect data on."
    **Must_Have_IP_Key_Value**, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
    **Must_Have_Intervention**, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
    **Has_Interventions**, array of strings, NA, NA, [], "A channel is added to the report for each intervention name specified. The channel value is the fraction of the population that has that intervention."
    **Include_30Day_Avg_Infection_Duration**, boolean, NA, NA, 1, "If set to true (1), the 30-Day Avg Infection Duration channel is included in the report."


.. code-block:: json

    {
        "Reports": [
            {
                "class": "ReportMalariaFilteredIntraHost",
                "Filename_Suffix": "kids_400",
                "Start_Day": 0,
                "End_Day": 3.40282e+38,
                "Node_IDs_Of_Interest": [],
                "Min_Age_Years": 0,
                "Max_Age_Years": 10,
                "Must_Have_IP_Key_Value": "",
                "Must_Have_Intervention": "",
                "Has_Interventions": [],
                "Include_30Day_Avg_Infection_Duration": 1
            }
        ],
        "Use_Defaults": 1
    }


Channels
========

The following channels are included in the report.

.. csv-table::
   :header: Channel, Description
   :widths: 15, 30

   30-day Avg Infection Duration, "The 30-day moving average of infection duration in days. Only included if **Include_30Day_Avg_Infection_Duration** is set to true."
   Avg Cytokines, "The average cytokine level per person across the population."
   Avg Num Infections, "The average number of simultaneous infections per person in the population."
   Blood Smear Parasite Prevalence, "The fraction of the population with a detectable parasite level based on a blood smear diagnostic."
   Campaign Cost, "The cumulative cost of campaigns distributed up to this time step."
   Fraction Infected, "The fraction of the statistical population that is currently infected."
   Inf Frac-Stage 1 - Hepatocyte, "The fraction of all active infections currently in the hepatocyte stage."
   Inf Frac-Stage 1 - Hepatocyte - New, "Of infections currently in the hepatocyte stage, the fraction that transitioned into that stage on this time step."
   Inf Frac-Stage 2 - Asexual, "The fraction of all active infections currently in the asexual blood stage."
   Inf Frac-Stage 2 - Asexual - New, "Of infections currently in the asexual stage, the fraction that transitioned into that stage on this time step."
   Inf Frac-Stage 3 - Gametocytes Only, "The fraction of all active infections currently in the gametocyte-only stage (asexual parasites cleared)."
   Inf Frac-Stage 3 - Gametocytes Only - New, "Of infections currently in the gametocyte-only stage, the fraction that transitioned into that stage on this time step."
   Infection Duration Max, "The duration in days of the longest-running active infection across all individuals at this time step."
   Max Inf-Avg Duration, "The average infection duration among individuals who are carrying the maximum allowed number of simultaneous infections."
   Max Inf-Pop Fraction, "The fraction of currently infected individuals who are carrying the maximum allowed number of simultaneous infections."
   New Clinical Cases, "The number of new clinical cases this time step."
   New Infections, "The number of new infections that began this time step."
   Statistical Population, "The total number of individuals in the simulation at this time step."
   True Prevalence, "The fraction of the population with at least one active infection, regardless of detectability."
   Variant Fraction-MSP, "The average fraction of MSP1 antibody variants present per person across the population."
   Variant Fraction-PfEMP1 Major, "The average fraction of PfEMP1 major epitope variants for which an individual has antibodies, averaged across the population."


Example
=======

The following is a sample of ReportMalariaFilteredIntraHost.json with 3 time steps.

.. literalinclude:: ../json/report-malaria-filtered-intra-host.json
   :language: json
