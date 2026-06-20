"""Operations for zeroing or modifying infections in humans and vectors."""

from __future__ import annotations

import logging
from typing import Any

from emod_api.serialization.dtk_file_support import NullPtr
from emod_api.serialization.serialized_population import SerializedPopulation

logger = logging.getLogger(__name__)

# VectorStateEnum (from VectorEnums.h)
STATE_INFECTIOUS = 0
STATE_INFECTED = 1
STATE_ADULT = 2
STATE_MALE = 3
STATE_IMMATURE = 4
STATE_LARVA = 5
STATE_EGG = 6

INFECTION_QUEUES = ("InfectiousQueues", "InfectedQueues", "AdultQueues")

UNINFECTED_HUMAN_TEMPLATE: dict[str, Any] = {
    "infections": [],
    "infectiousness": 0,
    "m_is_infected": False,
    "m_female_gametocytes": 0,
    "m_female_gametocytes_by_strain": [],
    "m_male_gametocytes": 0,
    "m_gametocytes_detected": 0,
    "m_new_infection_state": 0,
}


def zero_infections(
    ser_pop: SerializedPopulation,
    *,
    ignore_node_ids: list[int] | None = None,
    keep_individual_ids: list[int] | None = None,
    remove_vectors: bool = False,
) -> None:
    """Zero all infections in the loaded population (in-place).

    Resets human infection fields to uninfected state and either resets
    or removes infected vectors.

    Args:
        ser_pop: A loaded SerializedPopulation.
        ignore_node_ids: Node external IDs to skip entirely.
        keep_individual_ids: Individual SUID IDs whose infections are preserved.
        remove_vectors: If True, remove infected/infectious vector cohorts.
            If False (default), reset their state to STATE_ADULT.
    """
    if ignore_node_ids is None:
        ignore_node_ids = []
    if keep_individual_ids is None:
        keep_individual_ids = []

    for node in ser_pop.nodes:
        if node.externalId in ignore_node_ids:
            logger.info("Skipping node %s", node.externalId)
            continue

        logger.info("Zeroing infections in node %s", node.externalId)
        zero_vector_infections(node.m_vectorpopulations, remove=remove_vectors)
        zero_human_infections(node.individualHumans, keep_ids=keep_individual_ids)


def zero_human_infections(
    humans: Any,
    *,
    keep_ids: list[int] | None = None,
) -> int:
    """Reset infection state of individuals to uninfected.

    Args:
        humans: Iterable of individual dicts (e.g., ``node.individualHumans``).
        keep_ids: SUID IDs of individuals to skip.

    Returns:
        Number of individuals whose infections were zeroed.

    Raises:
        KeyError: If an individual is missing expected infection fields.
    """
    if keep_ids is None:
        keep_ids = []

    count = 0
    for person in humans:
        if person.suid.id in keep_ids:
            continue

        missing_keys = set(UNINFECTED_HUMAN_TEMPLATE) - set(person)
        if missing_keys:
            raise KeyError(
                f"Individual is missing expected infection fields: {missing_keys}"
            )
        person.update(UNINFECTED_HUMAN_TEMPLATE)
        count += 1

    return count


def zero_vector_infections(
    vector_pop_list: Any,
    *,
    remove: bool = False,
) -> int:
    """Reset or remove infections from vector populations.

    Args:
        vector_pop_list: List of vector populations
            (``node.m_vectorpopulations``).
        remove: If True, remove infected/infectious cohorts entirely.
            If False (default), reset to STATE_ADULT.

    Returns:
        Number of vector cohorts affected.
    """
    count = 0
    for idx, vector_population in enumerate(vector_pop_list):
        for queue in INFECTION_QUEUES:
            cohorts = vector_population[queue]["collection"]

            if remove:
                kept = [
                    c for c in cohorts
                    if c.state != STATE_INFECTED and c.state != STATE_INFECTIOUS
                ]
                removed = len(cohorts) - len(kept)
                vector_pop_list[idx][queue]["collection"] = kept
                count += removed
            else:
                for cohort in cohorts:
                    if cohort.state in (STATE_INFECTED, STATE_INFECTIOUS):
                        cohort.state = STATE_ADULT
                        cohort.progress = 0.0
                        cohort.m_pStrain = NullPtr()
                        count += 1

    return count
