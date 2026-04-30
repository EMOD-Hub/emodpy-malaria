=====================
ReportSimulationStats
=====================

The simulation statistics report is a CSV-formatted report that tracks performance and resource
usage data for each time step of the simulation. It records wall-clock timing, process memory,
system memory, and counts of key simulation objects (individuals, infections, interventions, and
events). This report is useful for diagnosing performance bottlenecks, monitoring memory growth over
the course of a simulation, and profiling how simulation size changes over time.

The report works with all simulation types and produces one row per time step per MPI rank.

This report is particularly useful when diagnosing unexpected slowdowns or memory growth. A common
workflow is to plot ``SimulationTime(Days)`` on the x-axis against ``TotalDuration(secs)`` or
``WorkingMemory(MB)`` on the y-axis — a sharp increase in slope indicates a time step where the
simulation became significantly slower or began consuming substantially more memory. Once you
identify the problem time step, inspect the other columns such as ``NumInterventionsAdded`` or
``NumIndividualEventsTriggered`` to see whether the change coincides with a spike in simulation
activity. You can then use ``SimulationTime(Days)`` to locate the corresponding event in your
campaign file and investigate whether a campaign event is responsible.


Configuration
=============

To generate this report, add the following to the custom_reports.json file. This report has no
configurable parameters beyond the class name.

.. code-block:: json

    {
        "Reports": [
            {
                "class": "ReportSimulationStats"
            }
        ],
        "Use_Defaults": 1
    }


Output file data
================

The output file is named ``ReportSimulationStats.csv``. The report contains the following columns.

.. csv-table::
    :header: Column, Data type, Description
    :widths: 15, 8, 30

    TotalDuration(secs), integer, "Total wall-clock time in seconds elapsed since the simulation process started."
    SimulationTime(Days), float, "The current simulation time in days."
    Rank, integer, "The MPI rank of the process that generated this row. In single-core runs this is always 0."
    StepDuration(secs), integer, "Wall-clock time in seconds taken to complete this time step."
    WorkingMemory(MB), float, "Current physical memory used by the simulation process, in megabytes. On Windows: Working Set Size. On Linux: Resident Set Size (VmRSS)."
    PeakWorkingMemory(MB), float, "Peak physical memory used by the simulation process since it started, in megabytes. On Windows: Peak Working Set Size. On Linux: Peak Resident Set Size (VmHWM)."
    VirtualMemory(MB), float, "Current virtual memory committed by the simulation process, in megabytes. On Windows: Pagefile Usage. On Linux: Virtual Memory Size (VmSize)."
    PeakVirtualMemory(MB), float, "Peak virtual memory committed by the simulation process since it started, in megabytes. On Windows: Peak Pagefile Usage. On Linux: Peak Virtual Memory Size (VmPeak)."
    FreeRAM(MB), float, "Free physical RAM available on the machine, in megabytes. On Windows: Available Physical Memory. On Linux: MemFree."
    TotalRAM(MB), float, "Total physical RAM installed on the machine, in megabytes. On Windows: Total Physical Memory. On Linux: MemTotal."
    FreeSwap(MB), float, "Free swap space available on the machine, in megabytes. On Windows: Available Page File. On Linux: SwapFree."
    TotalSwap(MB), float, "Total swap space available on the machine, in megabytes. On Windows: Total Page File. On Linux: SwapTotal."
    NumNodes, integer, "Number of nodes in the simulation at this time step."
    NumIndividuals, integer, "Total number of individuals across all nodes at this time step."
    NumInterventionsPersisted, integer, "Total number of active interventions currently held by all individuals at this time step."
    NumInterventionsAdded, integer, "Number of new interventions distributed to individuals during this time step."
    NumInfections, integer, "Total number of active infections across all individuals at this time step."
    NumIndividualEventsTriggered, integer, "Number of individual-level events triggered during this time step."
    NumIndividualEventsObserved, integer, "Number of individual-level events observed by event observers during this time step."


Example
=======

The following is an example of ReportSimulationStats.csv.

.. csv-table::
    :header: TotalDuration(secs),SimulationTime(Days),Rank,StepDuration(secs),WorkingMemory(MB),PeakWorkingMemory(MB),VirtualMemory(MB),PeakVirtualMemory(MB),FreeRAM(MB),TotalRAM(MB),FreeSwap(MB),TotalSwap(MB),NumNodes,NumIndividuals,NumInterventionsPersisted,NumInterventionsAdded,NumInfections,NumIndividualEventsTriggered,NumIndividualEventsObserved
    :widths: 3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3

    0,1,0,0,29,29,505,573,14669,32425,13364,35369,9,9000,0,0,0,29415,2396
    0,2,0,0,30,30,506,573,14658,32425,13352,35369,9,9000,0,0,0,22272,4251
    0,3,0,0,30,30,506,573,14652,32425,13345,35369,9,9000,0,0,0,21461,3436
    0,4,0,0,30,30,506,573,14652,32425,13348,35369,9,9000,0,0,0,20870,2846
    0,5,0,0,30,30,506,573,14650,32425,13249,35369,9,9000,0,0,0,20376,2347
    0,6,0,0,30,30,506,573,14638,32425,12763,35369,9,9000,0,0,0,20031,2006
    0,7,0,0,30,30,506,573,14632,32425,12844,35369,9,9000,0,0,0,19795,1776
    0,8,0,0,30,30,506,573,14624,32425,12833,35369,9,9000,0,0,0,19595,1572
    0,9,0,0,30,30,506,573,14614,32425,12834,35369,9,9000,0,0,0,19382,1349
    0,10,0,0,30,30,506,573,14614,32425,12831,35369,9,9000,0,0,0,19164,1142
