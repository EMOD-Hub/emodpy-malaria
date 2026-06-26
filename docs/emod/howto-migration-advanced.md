# How-to: Advanced migration

This page covers migration features beyond the basics in
[Tutorial 8](../tutorials/tutorial-8.md): explicit rates, age- and gender-dependent human
migration, and genetics-based vector migration.

**Related documentation:**

- [Geographic migration](model-migration.md) — conceptual overview of how EMOD models human and vector movement between nodes
- [Migration configuration parameters](parameter-configuration-migration.md) — config parameters controlling migration patterns, modes, and return times
- [Migration files](software-migration.md) — binary file format and JSON metadata structure
- [Vector migration](software-migration-vector.md) — vector-specific migration file details, including genetics-based migration
- [How to create migration files manually](software-migration-creation.md) — creating migration binaries from CSV/JSON using scripts
- [How to create vector migration files](software-migration-creation-vector.md) — creating vector migration binaries from CSV
- [Vector biology](vector-model-overview.md#spatial-scale-dynamics-and-migration) — vector migration in the context of the broader vector model
- [MigrateIndividuals](parameter-campaign-individual-migrateindividuals.md) — campaign intervention to force individual migration independently of the normal migration system
- [MigrateFamily](parameter-campaign-node-migratefamily.md) — campaign intervention to send family groups on round-trip migration
- [ReportHumanMigrationTracking](software-report-human-migration.md) — CSV report tracking individual human migration events
- [ReportVectorMigration](software-report-vector-migration.md) — CSV report tracking vector migration events

## Explicit rates (human migration)

When you have empirical data rather than a gravity fit, use `MigrationData.from_rates()`
with a dictionary of `{(from_node, to_node): rate}` pairs:

```python
from emodpy_malaria.migration import MigrationData, MigrationType

rates = {
    (1, 2): 0.05,
    (2, 1): 0.03,
    (1, 3): 0.01,
    (3, 1): 0.02,
    (2, 3): 0.02,
    (3, 2): 0.01,
}
human_mig = MigrationData.from_rates(rates, idref="my_simulation")
```

Rates must be in `[0.0, 1.0]` and are interpreted as daily probabilities of migrating from
one node to another (for small values, rates and probabilities are approximately equal).
For details on how EMOD uses these rates, see [Geographic migration](model-migration.md)
and [Migration configuration parameters](parameter-configuration-migration.md).

## Gender-specific rates

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
                                     idref="my_simulation")
```

The gravity model also supports gender-specific rates via `female_multiplier`, which scales
all female rates relative to the male rates:

```python
human_mig = MigrationData.from_gravity_model(demog, gravity_params,
                                             female_multiplier=0.5)
```

## Age-dependent rates

Migration rates often vary by age: children travel less, working-age adults travel more, and
the elderly travel less. There are three ways to create age-dependent migration data.

### Method 1: apply_modifier

Start from base rates (gravity model or explicit) and scale them with a callback function:

```python
regional_base = MigrationData.from_gravity_model(
    demog,
    gravity_params=[2e-06, 0.4, 0.5, -0.8]
)

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
group. The `ages` list defines the age boundaries in years. Rates returned by the modifier
are capped at 1.0 and zero-rate entries are dropped.

### Method 2: from_rates with ages

Provide a separate rate dictionary for each age group directly:

```python
child_rates = {(1, 2): 0.005, (2, 1): 0.003}
adult_rates = {(1, 2): 0.05, (2, 1): 0.03}
elder_rates = {(1, 2): 0.01, (2, 1): 0.008}

human_mig = MigrationData.from_rates(
    [child_rates, adult_rates, elder_rates],
    ages=[0, 15, 65],
    idref="my_simulation"
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
    idref="my_simulation"
)
```

This produces 6 layers (2 genders x 3 age groups), stored in gender-major, age-minor order
in the binary file.

### Method 3: MigrationData.combine

Merge independently constructed `MigrationData` objects (each with a single rate layer) into
one file. Useful when male and female rates come from completely different sources:

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
input `MigrationData` must have exactly one layer.

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

## Vector migration by allele combination

Gene-drive mosquitoes may disperse at different rates than wild-type. EMOD supports
genetics-based vector migration where each allele combination gets its own migration rate
layer. When a vector migrates, EMOD matches its genome against the allele combinations
(most specific first) and uses the corresponding rates. For background on vector migration
in EMOD, see [Vector migration](software-migration-vector.md) and the
[vector biology overview](vector-model-overview.md#spatial-scale-dynamics-and-migration).

`VectorMigrationData.from_genetics()` takes a dictionary where:

- **Keys** are tuples of allele pairs — each pair is `(allele1, allele2)`
- **Values** are rate dictionaries `{(from_node, to_node): rate}`
- The empty tuple `()` is **required** as the default (wild-type) fallback

```python
from emodpy_malaria.migration import VectorMigrationData

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

vector_mig = VectorMigrationData.from_genetics(allele_rates, idref="my_simulation")
```

Each key in the dictionary is a tuple of allele pairs that EMOD matches against a vector's
genome:

- `()` — matches any vector (the default fallback). This key is required.
- `(("a1", "X"),)` — matches vectors with allele `a1` paired with `X` at one locus.
- `(("a1", "a0"), ("b0", "b1"))` — matches vectors with allele pair `a1/a0` at one locus AND
  `b0/b1` at another. More specific combinations take priority.

Add it to demographics with `add_vector_migration()`:

```python
demog.add_vector_migration(
    data=vector_mig,
    species="gambiae",
    x_vector_migration=1.0
)
```

### Vector migration modifier parameters

Female vector migration can be influenced by environmental factors via modifier parameters
on `add_vector_migration()`:

| Parameter | Effect |
|-----------|--------|
| `x_vector_migration` | Scale factor applied to all migration rates |
| `vector_migration_habitat_modifier` | Preference toward nodes with more larval habitat |
| `vector_migration_food_modifier` | Preference toward nodes with more humans |
| `vector_migration_stay_put_modifier` | Preference to remain in the current node |
| `vector_migration_modifier_equation` | `LINEAR` (default) or `EXPONENTIAL` |

These modifiers apply only to female vectors.

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

## Migration file format

When the experiment runs, `add_migration()` and `add_vector_migration()` each write a binary
migration file with a JSON metadata sidecar. For full details on the file format, see
[Migration files](software-migration.md) (human) and
[Vector migration](software-migration-vector.md) (vector). The metadata includes fields that
tell EMOD which rate layer to use:

**Age/gender migration metadata:**

```json
{
    "Metadata": {
        "GenderDataType": "SAME_FOR_BOTH_GENDERS",
        "AgesYears": [0, 15, 65],
        "InterpolationType": "PIECEWISE_CONSTANT"
    }
}
```

**Genetics-based vector migration metadata:**

```json
{
    "Metadata": {
        "GenderDataType": "VECTOR_MIGRATION_BY_GENETICS",
        "AgesYears": [0, 1, 2],
        "AlleleCombinations": [
            [],
            [["a1", "X"]],
            [["a1", "a0"], ["b0", "b1"]]
        ]
    }
}
```

The `AgesYears` field (which has no meaning for vectors) is repurposed to store layer indices
for genetics-based migration.

## Key constraints

- Migration rates must be in `[0.0, 1.0]`.
- Migration to or from the default node (ID 0) is not allowed.
- Vector migration does not support age-dependent rates.
- The empty tuple `()` is required in `from_genetics()` as the default fallback.
- Allele combinations are sorted from least to most specific internally. EMOD evaluates most
  specific first.
- Modifier parameters (`habitat_modifier`, `food_modifier`, `stay_put_modifier`) apply only
  to female vectors.
