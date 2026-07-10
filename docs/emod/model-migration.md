# Geographic migration


Human migration is an important factor in the spread of disease across a geographic region. EMOD
represents geography using nodes. Migration occurs when individuals move from one *node* to
another; disease transmission occurs *within* nodes. Therefore, infected individuals can migrate to
nodes without disease and introduce disease transmission into that node. Nodes are very flexible and
can represent everything from individual households to entire countries or anything in between.
Therefore, to include migration in a simulation, you must define multiple nodes.

At each time step, individuals in each node have a defined rate of migration out of their
current node to another. You can also define the average length of time individuals will stay in
their destination node before migrating again. If you are using timesteps longer than one day and
the time to next migration falls between timesteps, individuals will migrate at the following
timestep. For example, if you use 7-day timesteps and an individual draws a 12-day trip duration,
they won't migrate until day 14.

The mode of migration can be local (foot travel), regional (by roadway or rail), by air, or by sea.
You can also define different migration patterns, such as one-way or roundtrip. Individuals have a
"home node" that is relevant for some types of migration, such as migrating an entire family unit
only when all members are home or returning home after passing through several waypoints. For more
detailed information, see [Migration configuration](parameter-configuration-migration.md) parameters.

For vector-borne diseases, you can also include vector migration. Both male and female vectors 
migrate. Each vector species has their own migration file. You can include additional rules for 
female vectors based on the availability of food or habitat.

You must include a separate migration file for each mode of travel that describes the migration
patterns for each node. It lists the migration rate for each node. Migration rate is defined as the
fraction of the node’s population that is migrating *out* of the node per day. Units are per person
per day, meaning the number of people migrating per day divided by the total population of the node.
For more information on the structure of these files, see [Migration creation](software-migration.md).

## Migration heterogeneity

By default, all individuals within a migration rate group (e.g., an age group in a node) share
the same migration rate. When **Enable_Migration_Heterogeneity** is set to true (1), each individual
is assigned a personal migration rate multiplier drawn from a configurable distribution at birth or
simulation initialization. This multiplier scales the individual’s overall migration rate for the
duration of their life, so some individuals migrate more frequently than others.

The distribution is configured in the demographics file using the **NodeAttributes** parameters
**MigrationHeterogeneityDistributionFlag**, **MigrationHeterogeneityDistribution1**, and
**MigrationHeterogeneityDistribution2**. Supported distribution types include constant, uniform,
Gaussian, exponential, Poisson, log normal, bimodal, and Weibull (flags 0–7). For example, setting
the flag to 0 (constant) with a value of 1 gives every individual the same rate (equivalent to
disabling heterogeneity), while setting the flag to 3 (exponential) produces a population where most
individuals migrate rarely and a few migrate frequently.

See [NodeAttributes](parameter-demographics.md#nodeattributes) for the demographics parameters and
[Migration configuration](parameter-configuration-migration.md) for the configuration parameter.

!!! note

    Migration heterogeneity applies only to human migration. Vector migration uses a separate system
    with its own modifiers (habitat, food, and stay-put) and is not affected by the human migration
    heterogeneity setting. See [Vector migration](software-migration-vector.md) for details.

