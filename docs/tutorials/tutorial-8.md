# Tutorial 8: Human and vector migration

This tutorial adds spatial movement to a multi-node simulation. It covers human migration
between nodes — including age- and gender-dependent rates — and vector migration that varies
by mosquito genotype using allele-combination layers. By the end you will have a working
simulation where people and vectors move between three nodes, with different migration rates
by age, sex, and mosquito genotype.

**File:** `tutorials/tutorial_8_migration.py`

## Why migration matters

Earlier tutorials used a single node. Real landscapes have multiple settlements connected by
human travel and mosquito dispersal. Human migration spreads parasites from high- to
low-transmission areas. Vector migration determines how quickly mosquito populations — and
their genes — spread across a landscape. Both are essential for modeling gene drives, focal
interventions, and importation risk.

## Demographics: three connected nodes

`build_demographics()` creates three nodes at different coordinates with different population
sizes. Nodes are passed to the `MalariaDemographics` constructor as a list of `Node` objects.
Larger and closer nodes will exchange more migrants under the gravity model.

```python
from emod_api.demographics.node import Node
from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
from emodpy_malaria.utils.distributions import ExponentialDistribution

def build_demographics():
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Village_A"),
        Node(lat=-2.1, lon=32.2, pop=2000, forced_id=2, name="Village_B"),
        Node(lat=-2.3, lon=32.5, pop=500,  forced_id=3, name="Village_C"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_8")

    demog.set_birth_rate(40)
    demog.set_age_distribution(ExponentialDistribution(20))
```

## Human migration

Human migration uses the `MigrationData` class from emodpy and the `add_migration()` method
on the demographics object. emodpy supports five migration types (LOCAL, REGIONAL, AIR, SEA,
FAMILY) and three movement patterns (RANDOM_WALK_DIFFUSION, SINGLE_ROUND_TRIPS,
WAYPOINTS_HOME).

### Gravity model

The gravity model computes migration rates from population sizes and distances:

    rate = g0 * from_pop^g1 * to_pop^g2 * distance_km^g3

Typical parameters use positive exponents for population and a negative exponent for distance,
so larger and closer nodes exchange more migrants.

```python
from emodpy_malaria.migration import MigrationData, MigrationType

gravity_params = [7.5e-06, 0.3, 0.6, -1.1]
human_mig = MigrationData.from_gravity_model(demog, gravity_params)
```

The four parameters are:

| Parameter | Role | Typical value |
|-----------|------|---------------|
| g0 | Overall scale | 7.5e-06 |
| g1 | Source population exponent | 0.3 |
| g2 | Destination population exponent | 0.6 |
| g3 | Distance exponent (negative = decay) | -1.1 |

### Adding migration to demographics

```python
demog.add_migration(
    data=human_mig,
    migration_type=MigrationType.LOCAL,
    migration_pattern="SINGLE_ROUND_TRIPS",
    roundtrip_duration=3.0,
    roundtrip_probability=0.9
)
```

`migration_type=MigrationType.LOCAL` registers this as local (short-range) migration.
`migration_pattern="SINGLE_ROUND_TRIPS"` means people travel to a destination and then return
home after `roundtrip_duration` days with probability `roundtrip_probability`.

### Explicit rates

When you have empirical data rather than a gravity fit, use `MigrationData.from_rates()`
with a dictionary of `{(from_node, to_node): rate}` pairs:

```python
rates = {
    (1, 2): 0.05,
    (2, 1): 0.03,
    (1, 3): 0.01,
    (3, 1): 0.02,
    (2, 3): 0.02,
    (3, 2): 0.01,
}
human_mig = MigrationData.from_rates(rates, idref="tutorial_8")
```

Rates must be in `[0.0, 1.0]` and represent the daily probability of migrating from one node
to another.

### Gender-specific rates

To give men and women different migration rates, pass `female_rates` to `from_rates()`.
This creates a `ONE_FOR_EACH_GENDER` migration file with two rate layers:

```python
male_rates = {
    (1, 2): 0.05, (2, 1): 0.03,
    (1, 3): 0.01, (3, 1): 0.02,
}
female_rates = {
    (1, 2): 0.02, (2, 1): 0.01,
    (1, 3): 0.005, (3, 1): 0.008,
}
human_mig = MigrationData.from_rates(male_rates, female_rates=female_rates,
                                     idref="tutorial_8")
```

The gravity model also supports gender-specific rates via `female_multiplier`, which scales
all female rates relative to the male rates:

```python
human_mig = MigrationData.from_gravity_model(demog, gravity_params,
                                             female_multiplier=0.5)
```

### Age-dependent rates

Migration rates often vary by age: children travel less, working-age adults travel more, and
the elderly travel less. There are three ways to create age-dependent migration data.

**Method 1: `apply_modifier`** — start from base rates (gravity model or explicit) and scale
them with a callback function. This is the approach used in `tutorial_8_migration.py`:

```python
regional_base = MigrationData.from_gravity_model(demog, [2e-06, 0.4, 0.5, -0.8])

def age_gender_modifier(base_rate, age, gender):
    MALE = 0
    if age < 15:
        return base_rate * 0.2       # children: 20% of base rate
    elif age < 65:
        if gender == MALE:
            return base_rate * 1.5   # working-age men: 150% of base rate
        return base_rate             # working-age women: base rate
    else:
        return base_rate * 0.3       # elderly: 30% of base rate

regional_mig = regional_base.apply_modifier(
    ages=[0, 15, 65],
    modifier_fn=age_gender_modifier
)
```

`apply_modifier()` calls `modifier_fn(base_rate, age, gender)` for every (node-pair, age,
gender) combination and produces a new `MigrationData` with one rate layer per age-gender
group. The `ages` list defines the age boundaries in years. If the base data is
`SAME_FOR_BOTH_GENDERS`, the modifier receives `gender=0` for every call; if it is
`ONE_FOR_EACH_GENDER`, it receives `0` (male) and `1` (female) separately.

Rates returned by the modifier are capped at 1.0 and zero-rate entries are dropped.

**Method 2: `from_rates` with `ages`** — provide a separate rate dictionary for each age
group directly:

```python
child_rates = {(1, 2): 0.005, (2, 1): 0.003}
adult_rates = {(1, 2): 0.05, (2, 1): 0.03}
elder_rates = {(1, 2): 0.01, (2, 1): 0.008}

human_mig = MigrationData.from_rates(
    [child_rates, adult_rates, elder_rates],
    ages=[0, 15, 65],
    idref="tutorial_8"
)
```

When `ages` is provided, `rates` must be a list of dictionaries — one per age boundary — in
the same order as `ages`. You can combine this with `female_rates` (also a list) to get
age-and-gender-specific layers:

```python
human_mig = MigrationData.from_rates(
    [child_m, adult_m, elder_m],
    female_rates=[child_f, adult_f, elder_f],
    ages=[0, 15, 65],
    idref="tutorial_8"
)
```

This produces 6 layers (2 genders x 3 age groups), stored in gender-major, age-minor order
in the binary file.

**Method 3: `MigrationData.combine`** — merge independently constructed `MigrationData`
objects (each with a single rate layer) into one file. Useful when male and female rates come
from completely different sources:

```python
from emodpy_malaria.migration import MigrationData
from emodpy.migration.migration_data import MALE, FEMALE

young_m = MigrationData.from_gravity_model(demog, [1e-4, 1, 1, -1])
old_m   = MigrationData.from_gravity_model(demog, [5e-5, 1, 1, -1])
young_f = MigrationData.from_gravity_model(demog, [8e-5, 1, 1, -1])
old_f   = MigrationData.from_gravity_model(demog, [3e-5, 1, 1, -1])

human_mig = MigrationData.combine({
    (MALE, 0):    young_m,
    (MALE, 30):   old_m,
    (FEMALE, 0):  young_f,
    (FEMALE, 30): old_f,
})
```

Each key is a `(gender, age)` tuple. All gender-age combinations must be present, and every
input `MigrationData` must have exactly one layer (no nested age/gender data).

### Adding age/gender migration to demographics

Adding age- or gender-dependent migration uses the same `add_migration()` call. The age and
gender structure is encoded in the binary file itself:

```python
demog.add_migration(
    data=regional_mig,
    migration_type=MigrationType.REGIONAL,
    user_notes="Age/gender regional migration"
)
```

You can add multiple migration types to the same demographics — for example, local migration
without age/gender layers and regional migration with them.

## Vector migration

Vector migration uses `VectorMigrationData` and is added via `add_vector_migration()` on
`MalariaDemographics`. It is configured per species and supports three modes:

| Mode | Description |
|------|-------------|
| Same for both genders | One rate layer applied to all vectors |
| One for each gender | Separate male and female rate layers |
| By genetics | One rate layer per allele combination |

### Basic vector migration

For uniform vector migration (no genetic differentiation), use the gravity model or explicit
rates just like human migration:

```python
from emodpy_malaria.migration import VectorMigrationData

vector_mig = VectorMigrationData.from_rates(
    rates={(1, 2): 0.1, (2, 1): 0.1, (1, 3): 0.05, (3, 1): 0.05,
           (2, 3): 0.08, (3, 2): 0.08}
)

demog.add_vector_migration(
    data=vector_mig,
    species="gambiae",
    x_vector_migration=1.0,
    vector_migration_habitat_modifier=3.0,
    vector_migration_food_modifier=0.0,
    vector_migration_stay_put_modifier=0.5
)
```

The modifier parameters control female vector preferences:

| Parameter | Effect |
|-----------|--------|
| `x_vector_migration` | Scale factor applied to all migration rates |
| `vector_migration_habitat_modifier` | Preference toward nodes with more larval habitat |
| `vector_migration_food_modifier` | Preference toward nodes with more humans |
| `vector_migration_stay_put_modifier` | Preference to remain in the current node |
| `vector_migration_modifier_equation` | `LINEAR` (default) or `EXPONENTIAL` |

### Vector migration by allele combinations

Gene-drive mosquitoes may disperse at different rates than wild-type. EMOD supports
genetics-based vector migration where each allele combination gets its own migration rate
layer. When a vector migrates, EMOD matches its genome against the allele combinations
(most specific first) and uses the corresponding rates.

`VectorMigrationData.from_genetics()` takes a dictionary where:

- **Keys** are tuples of allele pairs — each pair is `(allele1, allele2)`
- **Values** are rate dictionaries `{(from_node, to_node): rate}`
- The empty tuple `()` is **required** as the default (wild-type) fallback

```python
allele_rates = {
    # Default (wild-type): low migration
    (): {
        (1, 2): 0.01, (2, 1): 0.01,
        (1, 3): 0.005, (3, 1): 0.005,
        (2, 3): 0.008, (3, 2): 0.008,
    },

    # Vectors carrying one copy of the drive allele: moderate migration
    (("a1", "X"),): {
        (1, 2): 0.05, (2, 1): 0.05,
        (1, 3): 0.02, (3, 1): 0.02,
        (2, 3): 0.03, (3, 2): 0.03,
    },

    # Vectors homozygous for the drive allele: high migration
    (("a1", "a0"), ("b0", "b1")): {
        (1, 2): 0.10, (2, 1): 0.10,
        (1, 3): 0.05, (3, 1): 0.05,
        (2, 3): 0.08, (3, 2): 0.08,
    },
}

vector_mig_genetics = VectorMigrationData.from_genetics(allele_rates, idref="tutorial_8")
```

Each key in the dictionary is a tuple of allele pairs that EMOD matches against a vector's
genome:

- `()` — matches any vector (the default fallback). This key is required.
- `(("a1", "X"),)` — matches vectors with allele `a1` paired with `X` at one locus.
- `(("a1", "a0"), ("b0", "b1"))` — matches vectors with allele pair `a1/a0` at one locus AND
  `b0/b1` at another. More specific combinations take priority.

Add it to demographics the same way as basic vector migration:

```python
demog.add_vector_migration(
    data=vector_mig_genetics,
    species="gambiae",
    x_vector_migration=1.0,
    vector_migration_habitat_modifier=3.0,
    vector_migration_stay_put_modifier=0.5,
    user_notes="Gene-drive migration: wild-type low, heterozygous moderate, homozygous high"
)
```

The `user_notes` parameter is stored in the migration file's JSON metadata sidecar — use it
to record why the file was created.

### How allele matching works

EMOD evaluates allele combinations from most specific (most allele pairs) to least specific,
using the first match. The empty tuple `()` always matches, so it serves as the fallback for
any vector whose genome does not match a more specific combination.

The allele combinations are stored in the binary file's JSON metadata alongside a
`GenderDataType` of `VECTOR_MIGRATION_BY_GENETICS`. The `AgesYears` metadata field (which
has no meaning for vectors) is repurposed to store layer indices — one per allele combination.

## Putting it together

The complete `build_demographics()` function adds both human and vector migration:

```python
def build_demographics():
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Village_A"),
        Node(lat=-2.1, lon=32.2, pop=2000, forced_id=2, name="Village_B"),
        Node(lat=-2.3, lon=32.5, pop=500,  forced_id=3, name="Village_C"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_8")

    demog.set_birth_rate(40)
    demog.set_age_distribution(ExponentialDistribution(20))

    # --- Human migration (gravity model, round trips) ---
    gravity_params = [7.5e-06, 0.3, 0.6, -1.1]
    human_mig = MigrationData.from_gravity_model(demog, gravity_params)
    demog.add_migration(
        data=human_mig,
        migration_type=MigrationType.LOCAL,
        migration_pattern="SINGLE_ROUND_TRIPS",
        roundtrip_duration=3.0,
        roundtrip_probability=0.9
    )

    # --- Human migration (age/gender regional) ---
    regional_base = MigrationData.from_gravity_model(demog, [2e-06, 0.4, 0.5, -0.8])

    def age_gender_modifier(base_rate, age, gender):
        MALE = 0
        if age < 15:
            return base_rate * 0.2
        elif age < 65:
            if gender == MALE:
                return base_rate * 1.5
            return base_rate
        else:
            return base_rate * 0.3

    regional_mig = regional_base.apply_modifier(
        ages=[0, 15, 65],
        modifier_fn=age_gender_modifier
    )
    demog.add_migration(
        data=regional_mig,
        migration_type=MigrationType.REGIONAL,
        user_notes="Age/gender regional migration"
    )

    # --- Vector migration by allele combination ---
    allele_rates = {
        (): {
            (1, 2): 0.01, (2, 1): 0.01,
            (1, 3): 0.005, (3, 1): 0.005,
            (2, 3): 0.008, (3, 2): 0.008,
        },
        (("a1", "X"),): {
            (1, 2): 0.05, (2, 1): 0.05,
            (1, 3): 0.02, (3, 1): 0.02,
            (2, 3): 0.03, (3, 2): 0.03,
        },
        (("a1", "a0"), ("b0", "b1")): {
            (1, 2): 0.10, (2, 1): 0.10,
            (1, 3): 0.05, (3, 1): 0.05,
            (2, 3): 0.08, (3, 2): 0.08,
        },
    }
    vector_mig = VectorMigrationData.from_genetics(allele_rates, idref="tutorial_8")
    demog.add_vector_migration(
        data=vector_mig,
        species="gambiae",
        x_vector_migration=1.0,
        vector_migration_habitat_modifier=3.0,
        vector_migration_stay_put_modifier=0.5,
        user_notes="Gene-drive allele-based vector migration"
    )

    return demog
```

## Migration files

When the experiment runs, `add_migration()` and `add_vector_migration()` each write a binary
migration file with a JSON metadata sidecar. These are registered as task assets and uploaded
to the simulation automatically. The files look like:

```
local_migration.bin              # human local migration binary
local_migration.bin.json         # human local migration metadata
regional_migration.bin           # human regional migration binary (with AgesYears)
regional_migration.bin.json      # human regional migration metadata
vector_migration_gambiae.bin       # vector migration binary
vector_migration_gambiae.bin.json  # vector migration metadata (includes AlleleCombinations)
```

The regional migration metadata includes `AgesYears` and `GenderDataType` fields that tell
EMOD which rate layer to use for each age-gender group:

```json
{
    "Metadata": {
        "GenderDataType": "SAME_FOR_BOTH_GENDERS",
        "AgesYears": [0, 15, 65],
        "InterpolationType": "PIECEWISE_CONSTANT",
        ...
    }
}
```

When `apply_modifier` receives a base with `ONE_FOR_EACH_GENDER` data (e.g. from
`from_gravity_model` with `female_multiplier`), the output metadata will have
`GenderDataType: "ONE_FOR_EACH_GENDER"` and `AgesYears` will apply separately to each
gender's rate layers.

The vector metadata JSON for genetics-based migration includes an `AlleleCombinations` array
that maps each rate layer to its allele combination:

```json
{
    "Metadata": {
        "GenderDataType": "VECTOR_MIGRATION_BY_GENETICS",
        "AgesYears": [0, 1, 2],
        "AlleleCombinations": [
            [],
            [["a1", "X"]],
            [["a1", "a0"], ["b0", "b1"]]
        ],
        ...
    }
}
```

## Config callback

`build_config()` adds a vector species and defines the gene locus used by allele-based
migration. Migration config parameters (filenames, scale factors, modifier equations) are set
automatically by the implicit config functions registered by `add_migration()` and
`add_vector_migration()` — you do not need to set them manually.

```python
def build_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    # Add a gene locus with wild-type (a0) and drive (a1) alleles
    malaria_config.add_genes_and_alleles(
        config, manifest,
        species="gambiae",
        alleles=[("a0", 0.95), ("a1", 0.05)]
    )

    config.parameters.Simulation_Duration = 5 * 365
    config.parameters.Run_Number = 0
    return config
```

`add_genes_and_alleles()` adds a gene locus to the gambiae species with two alleles: `a0`
(wild-type, 95% initial frequency) and `a1` (drive allele, 5%). The allele names used here
must match the names in the allele combination keys passed to `VectorMigrationData.from_genetics()`.
Without this gene definition, EMOD would not recognize the allele names in the migration file.

## Loading existing migration files

If you have pre-built migration binaries from another tool or a previous run, load them
directly:

```python
# Human migration from file
demog.add_migration(
    data=MigrationData.from_migration_file("path/to/local_migration.bin"),
    migration_type=MigrationType.LOCAL
)

# Vector migration from file (including genetics-based)
demog.add_vector_migration(
    data=None,
    species="gambiae",
    vector_migration_filename_path="path/to/vector_migration_gambiae.bin"
)
```

`VectorMigrationData.from_migration_file()` also reads genetics-based files — it
reconstructs the allele combinations from the metadata sidecar automatically.

## Key constraints

- Migration rates must be in `[0.0, 1.0]`.
- Migration to or from the default node (ID 0) is not allowed.
- Vector migration does not support age-dependent rates.
- The empty tuple `()` is required in `from_genetics()` as the default fallback.
- Allele combinations are sorted from least to most specific internally. EMOD evaluates from
  most specific first.
- Modifier parameters (`habitat_modifier`, `food_modifier`, `stay_put_modifier`) apply only
  to female vectors.

## Next

[Tutorial 9](tutorial-9.md) adds site-specific weather data from binary files, replacing
constant climate with node-specific temperature, rainfall, and humidity time series.
