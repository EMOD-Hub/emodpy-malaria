# Tutorial 8: Human and vector migration

This tutorial adds spatial movement to a multi-node simulation. It covers human migration
using a gravity model and basic vector migration between nodes.

**File:** `tutorials/tutorial_8_migration.py`

## Why migration matters

In a spatial EMOD simulation, infections and parasites can only move between nodes if
infected people or mosquitoes physically move between them. If you set up a two-node
simulation and seed an outbreak in node 1, node 2 will never see any infections unless
people or mosquitoes migrate between the nodes. A multi-node simulation with no migration
is effectively multiple independent simulations — one per node — that happen to run inside
the same experiment. Migration is what connects the nodes together.

Human migration spreads parasites from high- to low-transmission areas. Vector migration
determines how quickly mosquito populations spread across a landscape. Both are essential
for modeling focal interventions, importation risk, and gene drives.

## Demographics: three connected nodes

`build_demographics()` creates three nodes at different coordinates with different population
sizes. Nodes are passed to the `MalariaDemographics` constructor as a list of `Node` objects.
Larger and closer nodes will exchange more migrants under the gravity model.

```python title="tutorial_8_migration.py, lines 66–82"
from emod_api.demographics.node import Node
from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
from emodpy_malaria.utils.distributions import UniformDistribution
from emodpy_malaria.utils.emod_enum import BirthRateDependence

def build_demographics():
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Village_A"),
        Node(lat=-2.1, lon=32.2, pop=2000, forced_id=2, name="Village_B"),
        Node(lat=-2.3, lon=32.5, pop=500,  forced_id=3, name="Village_C"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_8")

    demog.set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)
    demog.set_age_distribution(UniformDistribution(0, 60))
```

## Human migration: gravity model

The gravity model computes migration rates from population sizes and distances between nodes:

    rate = g0 * from_pop^g1 * to_pop^g2 * distance_km^g3

Typical parameters use positive exponents for population and a negative exponent for distance,
so larger and closer nodes exchange more migrants.

```python title="tutorial_8_migration.py, lines 88–98"
from emodpy_malaria.migration import MigrationData, MigrationType

gravity_params = [7.5e-06, 0.3, 0.6, -1.1]
human_mig = MigrationData.from_gravity_model(demog, gravity_params)

demog.add_migration(
    data=human_mig,
    migration_type=MigrationType.LOCAL,
    migration_pattern="SINGLE_ROUND_TRIPS",
    roundtrip_duration=3.0,
    roundtrip_probability=0.9
)
```

The four gravity parameters are:

| Parameter | Role | Typical value |
|-----------|------|---------------|
| g0 | Overall scale | 7.5e-06 |
| g1 | Source population exponent | 0.3 |
| g2 | Destination population exponent | 0.6 |
| g3 | Distance exponent (negative = decay) | -1.1 |

### Migration type

EMOD defines several migration types (LOCAL, REGIONAL, AIR, SEA, FAMILY). For most
simulations, use `MigrationType.LOCAL` — the other types are just names for additional
migration layers and don't change the underlying mechanics. What matters more is the
**movement pattern**: `SINGLE_ROUND_TRIPS` means people travel to a destination and return
home after `roundtrip_duration` days with probability `roundtrip_probability`.

### Rates

Migration rates are interpreted as daily probabilities of migrating from one node to another.
For the small rates typical in migration modeling, rates and probabilities are approximately
equal.

## Vector migration

Vector migration uses `VectorMigrationData` and is added via `add_vector_migration()` on
`MalariaDemographics`. It is configured per species.

For basic vector migration, use explicit rates — a dictionary of
`{(from_node, to_node): rate}` pairs:

```python title="tutorial_8_migration.py, lines 130–145"
from emodpy_malaria.migration import VectorMigrationData

vector_rates = {
    (1, 2): 0.01, (2, 1): 0.01,
    (1, 3): 0.005, (3, 1): 0.005,
    (2, 3): 0.008, (3, 2): 0.008,
}
vector_mig = VectorMigrationData.from_rates(rates=vector_rates)

demog.add_vector_migration(
    data=vector_mig,
    species="gambiae",
    x_vector_migration=1.0
)
```

`x_vector_migration` is a scale factor applied to all vector migration rates. Increasing it
makes vectors migrate more; setting it to 0 disables vector migration entirely.

## Config callback

`build_config()` adds a vector species. Migration config parameters (filenames, scale
factors) are set automatically by `add_migration()` and `add_vector_migration()` — you do
not need to set them manually.

```python title="tutorial_8_migration.py, lines 44–63"
def build_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    config.parameters.Simulation_Duration = 5 * 365
    config.parameters.Run_Number = 0
    return config
```

## Migration files

When the experiment runs, `add_migration()` and `add_vector_migration()` each write a binary
migration file with a JSON metadata sidecar. These are registered as task assets and uploaded
to the simulation automatically:

```
local_migration.bin              # human local migration binary
local_migration.bin.json         # human local migration metadata
vector_migration_gambiae.bin     # vector migration binary
vector_migration_gambiae.bin.json  # vector migration metadata
```

## Key constraints

- Migration rates must be in `[0.0, 1.0]`.
- Migration to or from the default node (ID 0) is not allowed.
- Vector migration does not support age-dependent rates.

## Next

For advanced migration features — explicit rates, age- and gender-dependent rates, and
genetics-based vector migration — see the
[Migration how-to](../emod/howto-migration-advanced.md).
