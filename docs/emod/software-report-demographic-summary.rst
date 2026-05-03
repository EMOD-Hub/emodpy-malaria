===================
DemographicsSummary
===================

The demographic summary output report (DemographicsSummary.json) is a JSON-formatted file with the
demographic :term:`channel` output results of the simulation, consisting of simulation-wide averages
by time step. The format is identical to the inset chart output report, except the channels reflect
demographic categories, such as gender ratio.

To generate the demographics summary report, set the **Enable_Demographics_Reporting** configuration
parameter to 1. The :doc:`software-report-binned` will also be generated.

The file contains a header and a channels section.

Header
======

The header section contains the following parameters.

.. csv-table::
   :header: Parameter, Data type, Description
   :widths: 10,5,15

   DateTime, string, The time stamp indicating when the report was generated.
   DTK_Version, string, The version of EMOD used.
   Report_Type, string, The type of output report.
   Report_Version, string, The format version of the report.
   Start_Time, integer, The time noted in days when the simulation begins.
   Simulation_Timestep, integer, The number of days in each time step.
   Timesteps, integer, The number of time steps in this simulation.
   Channels, integer, The number of channels in the simulation.


Channels
========

The channels section contains the following parameters.

.. csv-table::
   :header: Parameter, Data type, Description
   :widths: 7,5,10

   Average Age, integer, "The average age of the Statistical Population at each time step. This takes the age of each agent and multiplies it by the agent's Monte Carlo Weight, adds them together, then divides that sum by the Statistical Population."
   "Gender Ratio (fraction male)", integer, "The fraction of the statistical population that is male at each time step.  This takes the Monte Carlo weight of each male, adds them together, then divides by the statistical population."
   New Births, integer, "The statistical number of children born during each time step.  This is the sum of the Monte Carlo weight of each newborn."
   New Natural Deaths, integer, "The statistical number of people that died from natural causes (i.e. not disease) during each time step.  This is the sum of the Monte Carlo weights of each person that died."
   "Population Age X-Y", integer, "The statistical population of the people whose age is greater than or equal to X and strictly less than Y+1.  For example, if X=10 and Y=14, then if 10 <= age < 15, the person will be counted in that channel.  This channel is the sum of the Monte Carlo weight of each person that qualifies for that channel.  The set of channels is starts at 0-5 (i.e.<5) and increases every 5 years until the last bin is those people over 100."
   Possible Mothers, integer, The total number of females in the population whose age is greater than 14 years and less than 45 years.
   Pseudo-Population, integer, "The number of actual human agents in the simulation on that day. This number times the Monte Carlo Weight (which is controlled by the configuration parameter **Individual_Sampling_Type**) should be the same value as in the Statistical Population channel."
   Statistical Population, integer, "The total number of individuals in the simulation on that day. The sum of the Population Age X-Y channels at each time step should sum to this channel at the corresponding time step."


Example
=======

The following is a sample of a DemographicsSummary.json file.

.. literalinclude:: ../json/report-demographic.json
   :language: json