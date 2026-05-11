# Speed up EMOD simulations


While small simulations can be run quickly on a local computer, the time and memory needed to complete a
simulation can grow significantly when simulations become larger and more complex. For example, a
single geographical node simulation might use 3 GB with one core in order to run successfully in one
minute or less, while another simulation job may require 32 GB in a dual-core system in order to
complete in approximately the same amount of time.

As your simulations grow, you will likely want to run simulations on an HPC cluster or take other
steps to improve performance and reduce processing time. This topic describes many of the steps you
can take to speed up EMOD simulations.

## Parallel processing


EMOD supports parallel processing across multiple cores. When **Num_Cores** is set to a
value greater than 1 (but less than or equal to the number of nodes in the simulation),
emodpy-malaria will automatically run EMOD in parallel. This can significantly reduce
simulation time for large, spatially distributed simulations.

## Parameter settings


You can also set various parameters in the *configuration file* that will improve performance
by scaling down the amount of data used or optimizing data processing. See the parameters listed
in the sections below for guidance on making performance adjustments. See [parameter-configuration](parameter-configuration.md)
for more information about each of the parameters.

### Scaling and sampling


**Simulation_Duration**
    Obviously, simulating a shorter timespan will take less processing time. However, the
    processing time is often driven by the number of infections or immune updates, so running a
    simulation after all infections have cleared may not increase processing time much. For more
    information, see [Setup configuration](parameter-configuration-setup.md) parameters.
**Individual_Sampling_Type**
    Instead of the default **Individual_Sampling_Type** setting of "TRACK_ALL", you can speed up
    performance by sampling such that each individual object represents more than one person. For
    example, a simulation with a population of 1 million and sample rate of 0.1 would simulate
    100,000 individuals, with each given a weight of 10. Sampling can be fixed at a particular rate
    or can adapt the rate based on certain criteria, such as age or immune state. However, you
    should be especially careful not to undersample simulations to the point where they are overly
    sensitive to rare stochastic events. For more information, see [Sampling configuration](parameter-configuration-sampling.md)
    parameters.
**Population_Scale_Type** and **x_Base_Population**
    Alternatively, you can simply reduce the total population of the simulation using
    **Population_Scale_Type** set to "FIXED_SCALING" and **x_Base_Population** set to
    less than one. For more information, see [population configuration](parameter-configuration-population.md) parameters.

### Processing


**Num_Cores**
    For large, spatially distributed simulations, running the intra-node dynamics (for example,
    infection and immune dynamics) in parallel on multiple cores may be very advantageous. Ideally,
    the timing would be reduced inversely to the number of cores. However, there are costs to
    serializing individuals for migration over MPI, as well as considerations for balancing the CPU
    load on each core. These issues may be mitigated using a load balancing input file that is
    suitable to the geography being simulated. See [Load balancing](software-load-balancing.md) for more information.


### Vector and malaria


**Simulation_Type**
    "VECTOR_SIM" will run much faster than "MALARIA_SIM" if detailed intra-host dynamics are not
    "required.
**Vector_Sampling_Type** and **Mosquito_Weight**
    The individual vector simulation ("TRACK_ALL_VECTORS") will run more slowly than the cohort
    model ("VECTOR_COMPARTMENTS_NUMBER"). If the individual vector model must be used, you can
    improve performance by sampling some fraction of all vectors ("SAMPLE_IND_VECTORS") where
    each mosquito has a weight configured by **Mosquito_Weight**, which is analogous to
    individual human sampling.
**Infection_Updates_Per_Timestep**
    Using fewer intra-day updates to the malaria intra-host model will speed up simulation time.
    However, updates longer than three hours, such as eight per day, result in increasingly
    inaccurate dynamics.
