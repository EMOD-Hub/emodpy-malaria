===================
VectorSpeciesReport
===================

The vector species output report (VectorSpeciesReport.json) is a JSON-formatted file where the
channel data has been sorted into bins. It is identical to the :doc:`software-report-binned`, with
the exception that the bins are based on vector species, and provides the average number of adult
vectors per node for each species. The vector species report is generated for all malaria or vector
contain values in the **Vector_Species_Params** configuration parameter. For example, if
**Vector_Species_Params** contained "funestus" and "gambiae", you could be able to see the average
number of female vectors per node for both *A. funestus* and *A. gambiae*.

To generate this report, you must set **Enable_Vector_Species_Report** to 1 in the config.json file.



Header
======

The header section contains the following parameters.

.. csv-table::
   :header: Parameter, Data type, Description
   :widths: 7, 7, 20

   DateTime, string, The time stamp indicating when the report was generated.
   DTK_Version, string, The version of EMOD used.
   Report_Type, string, The type of output report.
   Report_Version, string, The format version of the report.
   Timesteps, integer, The number of timesteps in this simulation.
   Channels, integer, The number of channels in the simulation.
   Subchannel_Metadata, nested JSON object, "Metadata that describes the bins and axis information. The metadata includes the following parameters:

   .. list-table::
      :header-rows: 1

      * - Parameter
        - Data type
        - Description
      * - AxisLabels
        - array of strings
        - 'The name of the axis, Vector Species.'
      * - NumBinsPerAxis
        - array of integers
        - 'The number of bins per axis, one for each species.'
      * - ValuesPerAxis
        - array of integers
        - 'Not applicable for this report, always 0.'
      * - MeaningPerAxis
        - array of strings
        - 'The name of each species as defined in **Vector_Species_Params**.'

    "

Channels
========

The channels section contains the following parameters.

.. csv-table::
   :header: Parameter, Data type, Description
   :widths: 7, 5, 20

   <Channel_Title>, string, The title of the particular channel.
   Units, string, The units used for this channel.
   Data, array, A list of the channel data at each timestep.


The data channels included are:

.. csv-table::
  :header: Data channel, Description
  :widths: 10, 20

  Adult Vectors Per Node, "The average number of adult female vectors in each node on each day for each species."
  Fraction Infectious Vectors, "The fraction of adult female vectors that are infected and infectious."
  Daily EIR, "The entomological inoculation rate (EIR), or the number of infected mosquito bites each individual receives each day, on average."
  Daily HBR, "The average number of mosquito bites received per individual per day."
  Fraction Vectors Died Before Feeding, "The fraction of adult female vectors that die while attempting to feed indoors. This includes death before feeding (e.g. killed by a bednet), during feeding (e.g. squished = **Human_Feeding_Mortality**), and after feeding (e.g. landing on an IRS wall)."
  Fraction Vectors Died During Outdoor Feeding, "The fraction of vectors that die while attempting to feed outdoors. The causes are typically due to individual-level outdoor interventions."


Example
=======

The following is a sample of an VectorSpeciesReport.json file.

.. literalinclude:: ../json/report-vector-species2.json
   :language: json
