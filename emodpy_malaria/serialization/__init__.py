"""Malaria-specific utilities for working with EMOD .dtk serialized population files.

Builds on top of emod_api's SerializedPopulation with malaria-aware inspection,
modification, and export capabilities.

Example::

    from emodpy_malaria.serialization import (
        MalariaSerializedPopulation, zero_infections, count_humans
    )

    population = MalariaSerializedPopulation("state-00100.dtk")
    print(population.summary())
    print(count_humans(population.ser_pop))
    zero_infections(population.ser_pop)
    population.write("state-00100-zeroed.dtk")
"""

from emodpy_malaria.serialization._population import MalariaSerializedPopulation

from emodpy_malaria.serialization._infections import (
    zero_infections,
    zero_human_infections,
    zero_vector_infections,
    UNINFECTED_HUMAN_TEMPLATE,
    STATE_INFECTIOUS,
    STATE_INFECTED,
    STATE_ADULT,
    STATE_MALE,
    STATE_IMMATURE,
    STATE_LARVA,
    STATE_EGG,
    INFECTION_QUEUES,
)

from emodpy_malaria.serialization._genomes import (
    Genome,
    replace_genomes,
    get_all_barcodes,
    get_infection_barcodes,
)

from emodpy_malaria.serialization._inspect import (
    read_header,
    summarize,
    count_humans,
    count_infections,
    count_vectors,
    list_node_ids,
    find_parameter,
    get_all_parameters,
)

from emodpy_malaria.serialization._vectors import (
    VECTOR_STATE_NAMES,
    get_vector_species_names,
    count_vectors_by_state,
    get_vector_infection_summary,
)

from emodpy_malaria.serialization._export import (
    export_humans_to_json,
)

__all__ = [
    # wrapper class
    "MalariaSerializedPopulation",
    # infections
    "zero_infections",
    "zero_human_infections",
    "zero_vector_infections",
    "UNINFECTED_HUMAN_TEMPLATE",
    "STATE_INFECTIOUS",
    "STATE_INFECTED",
    "STATE_ADULT",
    "STATE_MALE",
    "STATE_IMMATURE",
    "STATE_LARVA",
    "STATE_EGG",
    "INFECTION_QUEUES",
    # genomes
    "Genome",
    "replace_genomes",
    "get_all_barcodes",
    "get_infection_barcodes",
    # inspect
    "read_header",
    "summarize",
    "count_humans",
    "count_infections",
    "count_vectors",
    "list_node_ids",
    "find_parameter",
    "get_all_parameters",
    # vectors
    "VECTOR_STATE_NAMES",
    "get_vector_species_names",
    "count_vectors_by_state",
    "get_vector_infection_summary",
    # export
    "export_humans_to_json",
]
