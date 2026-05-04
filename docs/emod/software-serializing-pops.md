# Serializing populations


Some simulations can take a long time to run and the part you are really interested in analyzing
isn't until closer to the end. You'd like to save the state of the simulation just before the
interesting stuff and then restart from that spot.  This would allow you to iterate more quickly on
different intervention strategies or just trying to understand what the simulation is doing better.
EMOD supports this ability with a feature called "serialized populations."

Serializing is the idea of saving the state of object so that there is enough information to
recreate that object later. Deserializing is the reverse, where you create a new object but
initialize it with the state that was saved.  For more information,  see
[serialization][wiki-serialization].  This is analogous to the sleep
feature in your computer: when you put it to sleep, it serializes data of the objects running the system;
when you start it back up again, it recreates what was running from that saved state.

The serialized population feature in EMOD allows you to save the state of the people and restart
from that saved state. This state includes the person's health, infections, any interventions that
they have, and more. This is especially useful when you need to create a population that has natural
immunity to a pathogen (i.e. the pathogen is not novel and the population is not naive.) It is important
to note that only events that have already occurred will be saved in the serialized population;  for
example, if the person has received only the first dose of a two dose vaccine when the
simulation was serialized, the person will only have that one dose when the simulation is
deserialized. The logic to give the person the second dose will still need to be added to the
simulation.

Being able to serialize the population is a powerful feature and can save the researcher lots of
time.  However, it does have it is idiosyncrasies.  The following information is intended to help
the user understand how serialization works, how to write a file, how to read from a serialized
file, and what parameters you can change when reading from a serialized file. For more information
on the format of serialized files, see [software-serialized](software-serialized.md).


## Example use cases


Serialization is useful for a variety of use-cases; we have outlined some common examples below.


### Try out different interventions (Simple burn-in)


To create a population with an endemic disease, one option is to start with a naïve population and
run simulation till disease dynamics reach an equilibrium. These *simulation burn-in* methods
can take several years of simulation time until a steady state is reached. Saving the state to a file
and continuing from this state reduces the time needed to model the effect of different interventions.

Burn-in is especially effective when exposure and individual immunity is age structured within the
population. For example, if older individuals have higher antibody levels than younger individuals,
due to prolonged exposure.


### Ultimate Report


In case existing reports don’t have what you need, a serialized population file contains all the
internal states of the people in the population.  By saving serialized population files periodically
and then extracting the data from these files, it is possible to gain very deep insights into the
simulation. The extracted “report data” can then be processed with dtk_post_process or analyzers
such that you only save the extracted data.  The serialized population files can be very big so you
could use this mechanism extract the data you want and then delete the large files.


### Reconfigure (currently only larval habitats)


When a simulation is saved to file and then loaded again, the state is exactly the same as it was at
the moment it was saved. There are options to reconfigure the simulation and read parameters from
config.json instead of the serialized file. This is called "masking" and is controlled by the
parameters **Serialization_Mask_Node_Write** and **Serialization_Mask_Node_Read**. These options are
currently very limited and only work
for larval habitats.


### Create a synthetic population


Sometimes you want to create a large spatial scenario but you don't want to wait to do burn-in just
to get a population with reasonable immune systems.  One way you could solve this problem is to run
a smaller one-node scenario that has a prevalence similar to the overall area you are trying to
model.  You do a burn-in with this smaller scenario to generate a representative population and
serialize that population at the end.  You could then use the people in this representative scenario
to generate a larger scenario and larger serialized file.

The state of all the individuals in a simulation is saved in a serialized population file. Python
libraries exist to manipulate the file and can be used to create, remove, or change attributes of an
individual.


### Calibration Chaining


You can calibrate for a first period of time and then save the file. From that starting point,
you can calibrate for the next period of time and so on.



## Serialized population file


The information below describes how serialized files work. For more information on formatting
serialized files, see [software-serialized](software-serialized.md).


### Internal state


A serialized population file contains the internal state of the objects used to create the
population in that realization. This internal state includes lots of implementation details that are
not really meant for user consumption.  With the right tools, you can open a file and look at its
contents.  The core of the information is in JSON format. For more detailed information, see
[software-serialized](software-serialized.md).

These implementation details are frequently the things that cause the data in the file to change.
When adding a new feature or fixing a bug, the developer might need to add new state to an object
that needs to be maintained from timestep to timestep.  This new state could be related to a new
model or something that just makes the model run faster.  Either way, this new information needs to
be written to and read from the file.  Hence, if you are updating from an older version to a newer
one, you will likely need to regenerate your serialized files.


### Population


The file contains the state of a human population and, for vector or malaria simulations, a vector
population. All the nodes that belong to the simulation and the individuals that belong to a node
are saved. Furthermore, each individual has an internal state and certain characteristics that
belong to it, like infections, drugs or interventions. Thus, interventions that were distributed
before the population was saved are still active. Node-level interventions or event coordinators are
not saved because they are not part of the population: they can change they state of a population
but are not part of it.

Similar to individuals, vectors and their habitats are saved.


### Multi-core


Serializing a simulation also works on a multi-core system: one file per core is written. To
continue the simulation all the created files must be defined in config.json and must use the same
number of cores.


### Upgrading to new executable


There is a strong dependency between the program code and the serialized file. Changing the EMOD
executable or modifying source code (especially removing, renaming or adding variables) will require
a rerun of the burn-in.


### File sizes


Serialized population files can be quite large - sometimes on the order of gigabytes.  This is
mostly impacted by the size of your population (and for vector or malaria simulations, the size of
the vector population).  Since the file already makes use of compression, compressing a serialized
file will provide minimal benefit.

The size of the file can become a memory issue when reading from the serialized file.  Reading large
files, for example over 5 gigabytes, requires a lot of memory to both read the file and create the
objects from that file.  The amount of RAM you have available for each of your simulations should
factor into how large of a file you want to use. If this is a concern, one can set the
parameter **logLevel_Memory** to DEBUG when running the simulation to serialize.  This will tell you
how much memory will be needed for the simulation after you read it back in.  However, it does not
include the memory needed to read the file.  If you are allowed 8-GB of memory per core, your
simulation is using 7-GB, and your file is 2-GB, you could be in danger of using more memory
than you are allowed.




