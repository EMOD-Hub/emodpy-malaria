"""Export serialized population data to external formats."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from emod_api.serialization.serialized_population import SerializedPopulation

logger = logging.getLogger(__name__)


def export_humans_to_json(
    ser_pop: SerializedPopulation,
    output_file: str | Path,
) -> None:
    """Export human data to a JSON file, grouped by node.

    Each key in the output JSON is ``"Node <external_id>"`` and the value
    is the list of individual dicts from that node.

    Args:
        ser_pop: A loaded SerializedPopulation.
        output_file: Destination JSON file path. Parent directories are
            created if they do not exist.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    human_data = {}
    for idx in range(len(ser_pop.nodes)):
        node = ser_pop.nodes[idx]
        human_data[f"Node {node.externalId}"] = node.individualHumans

    with open(output_path, "w") as f:
        json.dump(human_data, f)

    logger.info("Exported human data to %s", output_path)
