"""Read-only inspection and query functions for serialized populations."""

from __future__ import annotations

import difflib
import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import emod_api.serialization.dtk_file_tools as dft
from emod_api.serialization.serialized_population import SerializedPopulation

logger = logging.getLogger(__name__)


def read_header(file_path: str | Path) -> dict:
    """Read only the header of a .dtk file without loading node data.

    Useful for quickly checking file version, compression, node count,
    and EMOD build info without the cost of decompressing population data.

    Args:
        file_path (str | Path): Path to the .dtk file.

    Returns:
        Header dict with keys like ``version``, ``date``, ``author``,
        ``emod_info``, compression info, and chunk metadata.
    """
    with open(file_path, "rb") as handle:
        magic = handle.read(4).decode()
        if magic != dft.IDTK:
            raise ValueError(f"File has incorrect magic number: {magic!r}")

        size_string = handle.read(12)
        header_size = int(size_string)
        header_text = handle.read(header_size)
        header_json = json.loads(header_text.decode())

        if "metadata" in header_json:
            header_json = header_json["metadata"]
        if "version" not in header_json:
            header_json["version"] = 1

    return header_json


def summarize(ser_pop: SerializedPopulation) -> dict:
    """Return a comprehensive summary of the serialized population.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.

    Returns:
        Dict with ``num_nodes``, ``total_humans``, ``total_infections``,
        and a ``nodes`` list with per-node details.
    """
    nodes_info = []
    total_humans = 0
    total_infections = 0

    for idx in range(len(ser_pop.nodes)):
        node = ser_pop.nodes[idx]
        humans = node.individualHumans
        num_humans = len(humans)
        num_infections = sum(len(h["infections"]) for h in humans)
        num_infected = sum(1 for h in humans if h.get("m_is_infected", False))

        ages = [h.get("m_age", 0) for h in humans]
        mean_age = sum(ages) / len(ages) if ages else 0.0

        vector_pops = node.m_vectorpopulations
        species_names = []
        for vp in vector_pops:
            name = vp.get("m_species_id", vp.get("Species", "unknown"))
            species_names.append(str(name))

        nodes_info.append({
            "index": idx,
            "external_id": node.externalId,
            "num_humans": num_humans,
            "num_infections": num_infections,
            "num_infected_humans": num_infected,
            "mean_age_days": round(mean_age, 1),
            "num_vector_populations": len(vector_pops),
            "vector_species": species_names,
        })

        total_humans += num_humans
        total_infections += num_infections

    return {
        "num_nodes": len(ser_pop.nodes),
        "total_humans": total_humans,
        "total_infections": total_infections,
        "nodes": nodes_info,
    }


def count_humans(
    ser_pop: SerializedPopulation,
    *,
    node_index: int | None = None,
) -> int:
    """Count individuals across all nodes or in a specific node.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.
        node_index (int ): If provided, count only in this node (0-based index).

    Returns:
        Number of individuals.
    """
    if node_index is not None:
        return len(ser_pop.nodes[node_index].individualHumans)

    return sum(
        len(ser_pop.nodes[i].individualHumans)
        for i in range(len(ser_pop.nodes))
    )


def count_infections(
    ser_pop: SerializedPopulation,
    *,
    node_index: int | None = None,
) -> int:
    """Count total infections across all nodes or in a specific node.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.
        node_index (int ): If provided, count only in this node.

    Returns:
        Number of infections.
    """
    total = 0
    indices = [node_index] if node_index is not None else range(len(ser_pop.nodes))

    for idx in indices:
        node = ser_pop.nodes[idx]
        for human in node.individualHumans:
            total += len(human["infections"])

    return total


def count_vectors(
    ser_pop: SerializedPopulation,
    *,
    node_index: int | None = None,
    queue: str | None = None,
) -> int:
    """Count vector cohorts across all nodes or in a specific node.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.
        node_index (int ): If provided, count only in this node.
        queue (str ): If provided, count only in this queue (e.g.,
            ``"AdultQueues"``). If None, count across all queues.

    Returns:
        Number of vector cohorts.
    """
    from emodpy_malaria.serialization._infections import INFECTION_QUEUES

    queues_to_check = (queue,) if queue else INFECTION_QUEUES
    total = 0
    indices = [node_index] if node_index is not None else range(len(ser_pop.nodes))

    for idx in indices:
        node = ser_pop.nodes[idx]
        for vp in node.m_vectorpopulations:
            for q in queues_to_check:
                if q in vp:
                    total += len(vp[q]["collection"])

    return total


def list_node_ids(ser_pop: SerializedPopulation) -> list[int]:
    """Return the external IDs of all nodes.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.

    Returns:
        List of node external IDs.
    """
    return [ser_pop.nodes[i].externalId for i in range(len(ser_pop.nodes))]


def find_parameter(
    ser_pop: SerializedPopulation,
    name: str,
    *,
    cutoff: float = 0.6,
) -> list[str]:
    """Search for parameters matching the given name using fuzzy matching.

    Improved version of emod_api's ``find()`` that returns results as a list
    of dot-path strings instead of printing them.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.
        name (str): Parameter name to search for (e.g., ``"age"``, ``"gender"``).
        cutoff (float): Similarity threshold for fuzzy matching (0.0-1.0).

    Returns:
        List of dot-notation paths where the parameter was found.
    """
    results: list[str] = []
    _find_recursive(name, ser_pop.nodes, "nodes", cutoff, results)
    return results


def _find_recursive(
    name: str,
    handle: Any,
    current_level: str,
    cutoff: float,
    results: list[str],
) -> None:
    """Recursively search for a parameter name with fuzzy matching."""
    if isinstance(handle, str):
        if difflib.get_close_matches(name, [handle], cutoff=cutoff):
            results.append(current_level)
        return

    if not isinstance(handle, Iterable):
        return

    for idx, key in enumerate(handle):
        if isinstance(key, str):
            level = f"{current_level}.{key}"
        else:
            level = f"{current_level}[{idx}]"

        try:
            tmp = handle[key]
            if isinstance(tmp, Iterable) and not isinstance(tmp, str):
                _find_recursive(name, key, level, cutoff, results)
            else:
                _find_recursive(name, key, level, cutoff, results)
        except (KeyError, TypeError, IndexError):
            _find_recursive(name, key, level, cutoff, results)

        if isinstance(handle, dict):
            _find_recursive(name, handle[key], level, cutoff, results)


def get_all_parameters(ser_pop: SerializedPopulation) -> set[str]:
    """Return the set of all parameter paths in the serialized population.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.

    Returns:
        Set of dot-notation parameter paths.
    """
    return _get_params_recursive(ser_pop.nodes, "nodes")


def _get_params_recursive(
    handle: Any,
    current_level: str,
) -> set[str]:
    """Recursively collect parameter paths."""
    params: set[str] = set()

    if isinstance(handle, str):
        params.add(current_level)
        return params

    if not isinstance(handle, Iterable):
        return params

    for _, d in enumerate(handle):
        level = f"{current_level} {d}" if isinstance(d, str) else current_level
        params.update(_get_params_recursive(d, level))
        if isinstance(handle, dict):
            params.update(_get_params_recursive(handle[d], level))

    return params
