"""Inspection and modification of vector populations in serialized files."""

from __future__ import annotations

import logging
from typing import Any

from emod_api.serialization.serialized_population import SerializedPopulation

from emodpy_malaria.serialization._infections import (
    STATE_INFECTIOUS,
    STATE_INFECTED,
    STATE_ADULT,
    STATE_MALE,
    STATE_IMMATURE,
    STATE_LARVA,
    STATE_EGG,
    INFECTION_QUEUES,
)

logger = logging.getLogger(__name__)

VECTOR_STATE_NAMES: dict[int, str] = {
    STATE_INFECTIOUS: "Infectious",
    STATE_INFECTED: "Infected",
    STATE_ADULT: "Adult",
    STATE_MALE: "Male",
    STATE_IMMATURE: "Immature",
    STATE_LARVA: "Larva",
    STATE_EGG: "Egg",
}

_LIFECYCLE_QUEUES = (
    "EggQueues",
    "LarvaQueues",
    "ImmatureQueues",
    "MaleQueues",
    "AdultQueues",
    "InfectedQueues",
    "InfectiousQueues",
)


def _iter_nodes(ser_pop: SerializedPopulation, node_index: int | None):
    """Yield (index, node) pairs for the requested scope."""
    if node_index is not None:
        yield node_index, ser_pop.nodes[node_index]
    else:
        for idx in range(len(ser_pop.nodes)):
            yield idx, ser_pop.nodes[idx]


def get_vector_species_names(
    ser_pop: SerializedPopulation,
    *,
    node_index: int | None = None,
) -> list[str]:
    """Return the names of vector species present in the population.

    Args:
        ser_pop: A loaded SerializedPopulation.
        node_index: If given, inspect only this node. Otherwise inspects
            the first node (species are typically identical across nodes).

    Returns:
        List of species name strings.
    """
    idx = node_index if node_index is not None else 0
    node = ser_pop.nodes[idx]
    names = []
    for vp in node.m_vectorpopulations:
        name = vp.get("m_species_id", vp.get("Species", "unknown"))
        names.append(str(name))
    return names


def count_vectors_by_state(
    ser_pop: SerializedPopulation,
    *,
    node_index: int | None = None,
) -> dict[str, dict[str, int]]:
    """Count vector cohorts grouped by species and state.

    Args:
        ser_pop: A loaded SerializedPopulation.
        node_index: If given, count only this node. Otherwise sums all nodes.

    Returns:
        Nested dict: ``{species_name: {state_name: count, ...}, ...}``.
    """
    result: dict[str, dict[str, int]] = {}

    for _, node in _iter_nodes(ser_pop, node_index):
        for vp in node.m_vectorpopulations:
            species = str(vp.get("m_species_id", vp.get("Species", "unknown")))
            if species not in result:
                result[species] = {name: 0 for name in VECTOR_STATE_NAMES.values()}

            for queue_name in _LIFECYCLE_QUEUES:
                if queue_name not in vp:
                    continue
                queue_data = vp[queue_name]
                collection = queue_data.get("collection", queue_data) if isinstance(queue_data, dict) else queue_data
                if not hasattr(collection, '__len__'):
                    continue
                for cohort in collection:
                    state = cohort.get("state", None) if isinstance(cohort, dict) else getattr(cohort, "state", None)
                    if state is not None and state in VECTOR_STATE_NAMES:
                        result[species][VECTOR_STATE_NAMES[state]] += 1

    return result


def get_vector_infection_summary(
    ser_pop: SerializedPopulation,
    *,
    node_index: int | None = None,
) -> dict[str, Any]:
    """Summarize vector infection state across all species and queues.

    Args:
        ser_pop: A loaded SerializedPopulation.
        node_index: If given, summarize only this node.

    Returns:
        Dict with ``total_cohorts``, ``infected_cohorts``,
        ``infectious_cohorts``, ``total_oocyst_cohorts``,
        ``total_sporozoite_cohorts``, and a ``by_species`` breakdown.
    """
    total_cohorts = 0
    infected_cohorts = 0
    infectious_cohorts = 0
    total_oocysts = 0
    total_sporozoites = 0
    by_species: dict[str, dict[str, int]] = {}

    for _, node in _iter_nodes(ser_pop, node_index):
        for vp in node.m_vectorpopulations:
            species = str(vp.get("m_species_id", vp.get("Species", "unknown")))
            if species not in by_species:
                by_species[species] = {
                    "adult_count": 0,
                    "infected_count": 0,
                    "infectious_count": 0,
                }

            for queue in INFECTION_QUEUES:
                if queue not in vp:
                    continue
                cohorts = vp[queue]["collection"]
                for cohort in cohorts:
                    total_cohorts += 1
                    state = cohort.state if hasattr(cohort, "state") else cohort.get("state")
                    if state == STATE_INFECTED:
                        infected_cohorts += 1
                        by_species[species]["infected_count"] += 1
                    elif state == STATE_INFECTIOUS:
                        infectious_cohorts += 1
                        by_species[species]["infectious_count"] += 1
                    elif state == STATE_ADULT:
                        by_species[species]["adult_count"] += 1

                    oocysts = cohort.get("m_OocystCohorts", []) if isinstance(cohort, dict) else getattr(cohort, "m_OocystCohorts", [])
                    sporozoites = cohort.get("m_SporozoiteCohorts", []) if isinstance(cohort, dict) else getattr(cohort, "m_SporozoiteCohorts", [])
                    total_oocysts += len(oocysts)
                    total_sporozoites += len(sporozoites)

    return {
        "total_cohorts": total_cohorts,
        "infected_cohorts": infected_cohorts,
        "infectious_cohorts": infectious_cohorts,
        "total_oocyst_cohorts": total_oocysts,
        "total_sporozoite_cohorts": total_sporozoites,
        "by_species": by_species,
    }
