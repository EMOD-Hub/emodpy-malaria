# Creating and editing serialized populations


## Saving


To create and save serialized population files, configure the following parameters and then run a
simulation. The output serialized population file is a binary file that is saved with a name similar
to state-[timestamp].dtk, where [timestamp] is number of timesteps in the data file (e.g.
state-00100.dkt). Note that the size of the population impacts the size of the file, so working with
smaller populations will create smaller serialized files.


### Config parameters


The following configuration parameters must be set to create serialized files:

```
Serialized_Population_Writing_Type, enum, NONE, "The type of serialization to perform. NONE for no serialization; TIME to use the definition from Serialization_Times; and TIMESTEP to use definition from Serialization_Time_Steps."
Serialization_Times, array of floats, [], "The list of times at which to save the serialized state to file. 0 indicates the initial state before simulation, 'n' indicates the time to serialize in terms of start time and step size, rounded up to the nearest timestep.  Time is in term of days."
Serialization_Time_Steps, array of integers, [], "The list of timesteps after which to save the serialized state to file. 0 indicates the initial state before simulation, n indicates after the nth timestep.  "
Serialization_Mask_Node_Write, integer, 0, "A bitmask that defines what is NOT written to the file. O implies write everything to the file, 16 implies do NOT write larval habitats to the file."
Serialization_Precision, enum, REDUCED, "REDUCED is used to reduce the size of the serialized file. FULL give more floating point precision but creates larger files.  FULL precision is needed if you want the continuing simulation to be exactly the same as if you didn't start from a serialized file."
```

### Example JSON

The following example will save the population on day 50 and day 100.

[link](../json/software-serializing-create-1.json)

## Starting from


You include and use serialized population files in a simulation by configuring the following
parameters. If you do not specify an accurate path and filename, EMOD generates an error.



### Config parameters


The following configuration parameters must be set to create serialized files:

```
Serialized_Population_Reading_Type, enum, NONE, "Set to READ to enable reading from a serialized population file, set to NONE otherwise."
Serialized_Population_Path, string, empty string, "The root path for the serialized population files."
Serialized_Population_Filenames, array of strings, [],  "An array of filenames with serialized population data. The number of filenames must match the number of cores used for the simulation.  The path to the files is defined in **Serialized_Population_path**."
Serialization_Mask_Node_Read, integer, 0, "This is a bitmask to control what data is loaded.  0 implies loading all of the data in the serialized file.  16 implies that we do not load the larval habitat data from the serialized file and use the parameters in the configuration file instead."
Enable_Random_Generator_From_Serialized_Population, boolean, 0, "Determines if the random number generator should be extracted from a serialized population file. Enabling this (set to 1) starts a simulation from this file with the exact same random number stream and location in that stream as when the file was serialized."
```

### Example JSON


In this example a population is loaded from file ./my_files/state-00050.dtk. Everything saved in the file is read
("Serialization_Mask_Node_Read": 0).

[link](../json/software-serializing-create-2.json)

## Using larval habitats in the configuration file when reading from a serialized file


Sometimes when you are using a serialized file, you want to change the larval habitat for the vectors.
To do this, you first need to set the **Serialization_Mask_Node_Read** parameter to 16.  If there is habitat
data in the file, it will not be used.  The habitat you have configured in the configuration file will
be used instead.  WARNING: You MUST still have the same habitat types.  You can add new ones but you
you cannot remove them.  The eggs and larva that are in the file need a definition to go to.  However,
they will use the new parameter values (for example, for **Max_Larval_Capacity**).

If the serialized file was created without the habitat (**Serialization_Mask_Node_Write** = 16), then the
application will automatically generate habitat from the configuration parameters independent of setting
**Serialization_Mask_Node_Read** = 16.

## Manipulating


IDM provides a Python package [EMOD-Py](https://github.com/EMOD-Hub/emodpy-malaria)
with installation instructions and documentation to manipulate a serialized population file.

The following provides a list of a few scripts that are available in EMOD-Py.  Please see the package
for others and more details.

Remove all genomes - When using Full Parasite Genetics, this script will remove all of the genomes
from the existing infections.  This can be helpful when you want to replace existing genomes with new ones.

Remove all infections - Sometimes you want people to have developed immunity but want to control who
is infected when the simulation starts.  This script allows you to remove all the infections from the
humans (and vectors) so that you can determine who gets infected and when.

Remove all interventions - Like removing infections, you might just want a certain demographic of people
and their immunities but you want to determine what interventions they have.

Add/remove an individual property - Sometimes you need to add a new IP to the population in order to
implement a new intervention strategy.  If so, it is better to use a script and add the new IP to the
population.  This will ensure things work like you expect.

Modify vector habitat - You might have situation where there is a change in the environment like a
period of drought or extra long rainy season.  If so, you might want the ability to change the habitat
to reflect this environmental change.


## Changing parameters


When you are reading from a serialized file, you have a contention between what is in the serialized
file and what is in the input files.  Currently, there is not a good way to know what parameters you
can change and which ones you cannot.  This section is intended to provide some high level guidance.



