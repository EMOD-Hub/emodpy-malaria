# Tutorial: Working with serialized population data


This tutorial walks through common tasks with EMOD serialized population files
(`.dtk`) using the `emodpy_malaria.serialization` module. You will learn how to
open a file, inspect its contents, modify infections and parasite genomes, and
save the result.

For background on the binary file format, see
[Serialized population file](software-serialized.md). For EMOD configuration
parameters that control serialization, see
[Creating and editing serialized populations](software-serializing-create.md).


## Setup


All examples assume the following imports:

```python
from emodpy_malaria.serialization import (
    MalariaSerializedPopulation,
    read_header,
    count_humans,
    count_infections,
    count_vectors,
    list_node_ids,
    find_parameter,
    zero_infections,
    zero_human_infections,
    zero_vector_infections,
    replace_genomes,
    get_all_barcodes,
    get_infection_barcodes,
    get_vector_species_names,
    count_vectors_by_state,
    get_vector_infection_summary,
    export_humans_to_json,
    Genome,
)
```


## Opening a file


Load a `.dtk` file with `MalariaSerializedPopulation`. This decompresses the
data and gives you access to the full population:

```python
population = MalariaSerializedPopulation("state-00100.dtk")

# MalariaSerializedPopulation(file='state-00100.dtk', version=6, nodes=1)
```

The object exposes properties for navigating the data:

| Property | Type | Description |
|---|---|---|
| `population.ser_pop` | SerializedPopulation | The underlying emod_api object (passed to standalone functions) |
| `population.nodes` | list | All nodes in the file |
| `population.simulation` | dict | Simulation-level state |
| `population.header` | dict | File header metadata (version, compression, dates) |
| `population.version` | int | DTK file format version (1–6) |
| `population.num_nodes` | int | Number of nodes |
| `population.file_path` | Path | Original file path |

And methods that depend on internal state tracking:

| Method | Returns | Description |
|---|---|---|
| `population.summary()` | dict | Node counts, human counts, infection counts, vector species |
| `population.find_parameter(name)` | list[str] | Fuzzy search for parameter names, returns dot-paths |
| `population.get_next_infection_suid()` | dict | Generate a unique SUID for a new infection |
| `population.get_next_individual_suid(node_id)` | dict | Generate a unique SUID for a new individual |
| `population.write(output_file)` | None | Save the (possibly modified) population to a `.dtk` file |


## Inspecting without loading


Read metadata from a `.dtk` file without decompressing the population data.
This is fast even for multi-gigabyte files:

```python
header = read_header("state-00100.dtk")
print(header["version"])           # 6
print(header["date"])              # "Mon Jan 01 00:00:00 2025"
print(header["sim_compression"])   # "LZ4"
print(len(header["node_suids"]))   # Number of nodes
```


## Getting a population summary


```python
population = MalariaSerializedPopulation("state-00100.dtk")
summary = population.summary()
print(summary)
```

Returns a dict like:

```python
{
    "num_nodes": 1,
    "total_humans": 1000,
    "total_infections": 423,
    "nodes": [
        {
            "index": 0,
            "external_id": 340461476,
            "num_humans": 1000,
            "num_infections": 423,
            "num_infected_humans": 312,
            "mean_age_days": 7300.5,
            "num_vector_populations": 1,
            "vector_species": ["arabiensis"],
        }
    ],
}
```


## Counting and listing


All counting functions take `population.ser_pop` as their first argument:

```python
count_humans(population.ser_pop)                  # Total across all nodes
count_humans(population.ser_pop, node_index=0)    # In a specific node

count_infections(population.ser_pop)              # Total infections
count_infections(population.ser_pop, node_index=0)

count_vectors(population.ser_pop)                             # All vector cohorts
count_vectors(population.ser_pop, queue="InfectiousQueues")   # Only infectious

list_node_ids(population.ser_pop)    # [340461476, 340461477, ...]
```


## Navigating the data hierarchy


A serialized population file contains nested data at five levels. Each level
is accessible as a dict-like object that supports both attribute access
(`individual.m_age`) and dictionary access (`individual["m_age"]`). The
attribute form is recommended for readability.


### Simulation level

```python
sim = population.simulation
```

| Field | Description |
|---|---|
| `sim.infectionSuidGenerator` | Tracks next unique infection ID. Contains `next_suid` and `numtasks`. |
| `sim.ParasiteGenetics` | Parasite genetics configuration including `m_ParasiteGenomeMap`. |


### Node level

```python
node = population.nodes[0]
node_id = node.externalId
```

| Field | Description |
|---|---|
| `node.externalId` | External node identifier |
| `node.individualHumans` | All human individuals in this node |
| `node.m_vectorpopulations` | Vector (mosquito) populations, one per species |
| `node.m_IndividualHumanSuidGenerator` | Tracks next unique individual ID for this node |


### Individual level

```python
individual = population.nodes[0].individualHumans[0]
```

| Field | Type | Description |
|---|---|---|
| `individual.suid.id` | int | Unique individual identifier |
| `individual.m_age` | float | Age in days |
| `individual.m_gender` | int | Gender (0 = male, 1 = female) |
| `individual.m_is_infected` | bool | Whether the individual has any active infection |
| `individual.infectiousness` | float | Current infectiousness to vectors |
| `individual.infections` | list | Active infection objects |
| `individual.susceptibility` | dict | Immune state: antibody levels, modifiers for acquisition, transmission, and mortality |
| `individual.m_female_gametocytes` | int | Total female gametocyte count |
| `individual.m_male_gametocytes` | int | Total male gametocyte count |
| `individual.m_female_gametocytes_by_strain` | list | Female gametocytes broken down by parasite strain |
| `individual.m_gametocytes_detected` | int | Whether gametocytes have been detected |
| `individual.m_new_infection_state` | int | State flag for newly acquired infections |


### Infection level

```python
infection = individual.infections[0]
genome = infection.infection_strain.m_Genome.m_pInner
```

| Field | Type | Description |
|---|---|---|
| `infection.suid` | dict | Unique infection identifier (`{"id": int}`) |
| `infection.infection_strain` | dict | Strain identity containing the parasite genome |
| `genome.m_HashCode` | int | Combined hash of nucleotides and allele roots |
| `genome.m_BarcodeHashcode` | int | Hash of the nucleotide barcode only |
| `genome.m_NucleotideSequence` | list[int] | Barcode as integers (0=A, 1=C, 2=G, 3=T) |
| `genome.m_AlleleRoots` | list[int] | Allele root IDs for each nucleotide position |


### Vector populations

Each node contains one or more vector populations, one per mosquito species:

```python
vector_pop = node.m_vectorpopulations[0]
species_name = vector_pop.m_species_id
```

**Lifecycle queues:**

Each queue holds a list of vector cohorts in its `.collection` attribute.
For example, `vector_pop.AdultQueues.collection` is a list where each element
is a cohort with the fields described below.

| Queue | Contents |
|---|---|
| `vector_pop.EggQueues.collection` | Egg cohorts |
| `vector_pop.LarvaQueues.collection` | Larval cohorts |
| `vector_pop.ImmatureQueues.collection` | Immature adult cohorts |
| `vector_pop.MaleQueues.collection` | Male cohorts |
| `vector_pop.AdultQueues.collection` | Adult female cohorts |
| `vector_pop.InfectedQueues.collection` | Infected (oocyst-stage) cohorts |
| `vector_pop.InfectiousQueues.collection` | Infectious (sporozoite-stage) cohorts |

**Vector cohort fields:**

Each element in a queue's `collection` is a cohort object. Access fields
with attribute syntax:

```python
for cohort in vector_pop.AdultQueues.collection:
    print(cohort.state, cohort.progress)
```

| Field | Type | Description |
|---|---|---|
| `cohort.state` | int | Lifecycle state: 0=Infectious, 1=Infected, 2=Adult, 3=Male, 4=Immature, 5=Larva, 6=Egg |
| `cohort.progress` | float | Progress through current state (0.0 to 1.0) |
| `cohort.m_pStrain` | dict or null | Strain identity (null for uninfected vectors) |
| `cohort.m_OocystCohorts` | list | Oocyst-stage parasite cohorts within this vector |
| `cohort.m_SporozoiteCohorts` | list | Sporozoite-stage parasite cohorts within this vector |

**Oocyst and sporozoite cohort fields:**

| Field | Description |
|---|---|
| `oocyst.m_MaleGametocyteGenome` | Male gametocyte genome (same structure as infection genomes) |
| `oocyst.m_pStrainIdentity.m_Genome` | Female gametocyte genome |


## Inspecting vectors

```python
get_vector_species_names(population.ser_pop)
# ["arabiensis", "funestus"]

count_vectors_by_state(population.ser_pop)
# {"arabiensis": {"Adult": 5000, "Infected": 120, "Infectious": 45, ...}, ...}

get_vector_infection_summary(population.ser_pop)
# {"total_cohorts": 5165, "infected_cohorts": 120, "infectious_cohorts": 45,
#  "total_oocyst_cohorts": 240, "total_sporozoite_cohorts": 90, "by_species": {...}}
```


## Finding parameters by name

Search for parameters using fuzzy matching:

```python
population.find_parameter("age")
# ["nodes[0].individualHumans[0].m_age",
#  "nodes[0].individualHumans[0].susceptibility.age",
#  "nodes[0].m_vectorpopulations[0].EggQueues.collection[0].age", ...]
```


## Zeroing infections


Remove all infections from humans and vectors. This is commonly used to prepare
a burn-in population for a pickup simulation where you control initial
infections:

```python
population = MalariaSerializedPopulation("state-00100.dtk")

zero_infections(population.ser_pop)
population.write("state-00100-zeroed.dtk")
```

### Options

```python
# Skip specific nodes (by external ID)
zero_infections(population.ser_pop, ignore_node_ids=[340461476])

# Keep infections in specific individuals (by SUID)
zero_infections(population.ser_pop, keep_individual_ids=[42, 99])

# Remove infected vectors entirely instead of resetting their state
zero_infections(population.ser_pop, remove_vectors=True)
```

### Fine-grained control

For per-node control, use the lower-level functions directly on node data:

```python
node = population.nodes[0]

zeroed_count = zero_human_infections(node.individualHumans)
print(f"Zeroed infections in {zeroed_count} individuals")

vector_count = zero_vector_infections(node.m_vectorpopulations, remove=False)
print(f"Reset {vector_count} vector cohorts")
```


## Inspecting parasite genetics


```python
# All unique barcodes in the population's genome map
barcodes = get_all_barcodes(population.ser_pop)
# ["AACGTACG...", "CCGTAACG...", ...]

# Per-infection barcode details
infections = get_infection_barcodes(population.ser_pop, node_index=0)
for inf in infections[:3]:
    print(f"Individual {inf['individual_id']}: {inf['barcode']}")
```


## Replacing parasite genomes


Replace all parasite genomes with new barcodes. Provide a callable that
returns the next barcode string each time it is called:

```python
barcode_index = 0
barcodes = ["AACGTACGTACGTACGTACGTACGT", "CCGTAACGTACGTACGTACGTACGT"]

def get_next_barcode():
    global barcode_index
    barcode = barcodes[barcode_index % len(barcodes)]
    barcode_index += 1
    return barcode

population = MalariaSerializedPopulation("state-00100.dtk")
count = replace_genomes(population.ser_pop, get_next_barcode)
print(f"Replaced {count} genomes")
population.write("state-00100-new-genomes.dtk")
```


### Working with the Genome class

Inspect or create genome objects directly:

```python
# Create a genome
genome = Genome("AACGTACGT", allele_root_id=42)
print(genome.barcode)         # "AACGTACGT"
print(genome.hashcode)        # integer hash code
dtk_dict = genome.to_dtk_dict()   # DTK-format dict with m_pInner

# Reconstruct from a DTK dict found in the population
individual = population.nodes[0].individualHumans[0]
existing = individual.infections[0].infection_strain.m_Genome
genome = Genome.from_dtk_dict(existing)
print(genome.barcode)
```


## Modifying individual properties


Access and modify fields on individuals directly:

```python
for node in population.nodes:
    for individual in node.individualHumans:
        # Read fields
        age_years = individual.m_age / 365.0
        is_infected = individual.m_is_infected

        # Modify fields
        individual.m_age = individual.m_age + 365.0  # Age everyone by one year

        # Modify susceptibility
        individual.susceptibility.mod_acquire = 0.5
```


## Adding and removing individuals


Remove individuals by filtering:

```python
import copy

node = population.nodes[0]

# Keep only adults (age > 5 years)
node.individualHumans = [
    ind for ind in node.individualHumans
    if ind.m_age > 5 * 365
]
```

Add a new individual by copying and modifying an existing one:

```python
template = copy.deepcopy(node.individualHumans[0])
template.suid = population.get_next_individual_suid(0)
template.m_age = 3650.0  # 10 years old
node.individualHumans.append(template)
```


## Adding infections to an individual


```python
import copy

source_individual = node.individualHumans[0]
target_individual = node.individualHumans[1]

new_infection = copy.deepcopy(source_individual.infections[0])
new_infection.suid = population.get_next_infection_suid()
target_individual.infections.append(new_infection)
target_individual.m_is_infected = True
```


## Exporting data


### JSON export

Export all human data to a JSON file, grouped by node:

```python
export_humans_to_json(population.ser_pop, "humans_data.json")
```

The output JSON has the structure:

```json
{
    "Node 340461476": [ ... list of individual dicts ... ],
    "Node 340461477": [ ... ]
}
```


### Extracting fields for analysis

Pull specific fields into Python data structures:

```python
ages = []
gametocyte_counts = []

for node in population.nodes:
    for individual in node.individualHumans:
        ages.append(individual.m_age / 365.0)
        gametocyte_counts.append(individual.m_female_gametocytes)

import pandas as pd
df = pd.DataFrame({"age_years": ages, "female_gametocytes": gametocyte_counts})
```


## Saving changes


After making any modifications, write the population to a new file:

```python
population.write("state-00100-modified.dtk")
```

!!! note
    Always write to a **new file** rather than overwriting the original. This
    preserves the original burn-in state in case you need to go back to it or
    make different modifications.

The `write` method automatically creates parent directories if they do not
exist, flushes pending node changes, and updates the infection SUID generator
in the simulation header.
