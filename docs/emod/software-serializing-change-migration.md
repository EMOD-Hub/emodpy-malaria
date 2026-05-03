# Changing serialized migration parameters



Not every parameter can be changed after the creation of serialized files. The following overview
is intended as high-level guidance for what changes can and cannot be made.



## Migration_Model


* *ON-to-OFF*: If you turn it off, there will be no human migration even if the serialized file had trips planned or people were waiting to return.
* *OFF-to-ON*:

    * If the file was serialized with migration off, and you set the **Migration_Model** to FIXED_RATE_MIGRATION and set **Migration_Pattern** to SINGLE_ROUND_TRIPS/RANDOM_WALK_DIFFUSION, then the migration will work as expected.

    * If the file was serialized with migration off, and you set **Migration_Pattern** = WAYPOINTS_HOME, then the serialized people will be fixed at one waypoint. Newborns will get the value of **Roundtrip_Waypoints**, but not the serialized people.

## Migration_Pattern


This cannot be serialized.  Changing the value will change behavior but not in a guaranteed way.
For example, if you change it from SINGLE_ROUND_TRIPS to WAYPOINTS_HOME, **Roundtrip_Waypoints**
is always 1 for the people that were serialized.  Newborns should get the new value.

Note that while the type of **Migration_Pattern** cannot be changed, other migration parameters
*can* be changed under specific circumstances.


### Migration_Pattern = SINGLE_ROUND_TRIPS


The following parameters can be changed as long as **Migration_Pattern** was serialized as SINGLE_ROUND_TRIPS.
Changing this parameter will not impact those people who have determined their return trip
before the file was serialized.  After de-serializing, new decisions to return will use
these parameters.

* **Air_Migration_Roundtrip_Probability**
* **Family_Migration_Roundtrip_Probability**
* **Local_Migration_Roundtrip_Probability**
* **Regional_Migration_Roundtrip_Probability**
* **Sea_Migration_Roundtrip_Probability**
* **Air_Migration_Roundtrip_Duration**
* **Family_Migration_Roundtrip_Duration**
* **Local_Migration_Roundtrip_Duration**
* **Regional_Migration_Roundtrip_Duration**
* **Sea_Migration_Roundtrip_Duration**


## Enable_X_Migration


This includes the parameters **Enable_Local_Migration**, **Enable_Region_Migration**,
**Enable_Air_Migration**, **Enable_Sea_Migration**, and **Enable_Family_Migration**.

* *ON-to-OFF*: If **Migration_Model** = FIXED_RATE_MIGRATION and you turn these off, existing plans for migration - both out and return - will still occur.  However, no new migration plans will be made.
* *OFF-to-ON*: People should start migrating as designed.


## Roundtrip_Waypoints


This can be changed under certain circumstances.  If you serialized with **Migration_Pattern**
set to WAYPOINTS_HOME, you can change this but it will NOT change the number of waypoints
for the people that were serialized.  All the people being born after de-serializing will
receive the new number of waypoints.




## Vector migration


Vector migration can be changed when reading from a serialized file.  Vectors migrate
differently then humans: each timestep a vector considers migrating; if they decide
to migrate, they then go to the new node.  They do not save state.  Hence, if you turn it on or
off, vectors will act like the new situation was always this way.  NOTE however that  Only female
adult vectors migrate.

The following parameters can be changed:

* **Enable_Vector_Migration**
* **Enable_Vector_Migration_Local**
* **Enable_Vector_Migration_Regional**
* **Vector_Migration_Filename_Local**
* **Vector_Migration_Filename_Regional**
* **Vector_Migration_Modifier_Equation**
* **Vector_Migration_Food_Modifier**
* **Vector_Migration_Habitat_Modifier**
* **Vector_Migration_Stay_Put_Modifier**
* **x_Vector_Migration_Local**
* **x_Vector_Migration_Regional**