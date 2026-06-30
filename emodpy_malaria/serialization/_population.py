"""MalariaSerializedPopulation: malaria-aware wrapper around SerializedPopulation."""

from __future__ import annotations

import logging
from pathlib import Path
from emod_api.serialization.serialized_population import SerializedPopulation

logger = logging.getLogger(__name__)


class MalariaSerializedPopulation:
    """Malaria-aware wrapper around emod_api's SerializedPopulation.

    Provides malaria-specific convenience methods for inspection,
    modification, and export of ``.dtk`` serialized population files.
    Delegates to the underlying SerializedPopulation for all low-level
    file I/O.

    Args:
        file_path (str | Path): Path to a ``.dtk`` serialized population file.
    """

    def __init__(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)
        self._ser_pop = SerializedPopulation(str(self._file_path))

    @property
    def ser_pop(self) -> SerializedPopulation:
        """The underlying emod_api SerializedPopulation object."""
        return self._ser_pop

    @property
    def file_path(self) -> Path:
        """Original file path."""
        return self._file_path

    @property
    def nodes(self):
        """All nodes (delegated to SerializedPopulation.nodes)."""
        return self._ser_pop.nodes

    @property
    def simulation(self):
        """Simulation-level data dict."""
        return self._ser_pop.dtk.simulation

    @property
    def header(self):
        """File header metadata."""
        return self._ser_pop.dtk.header

    @property
    def version(self) -> int:
        """DTK file format version."""
        return self._ser_pop.dtk.header.version

    @property
    def num_nodes(self) -> int:
        """Number of nodes in the file."""
        return len(self._ser_pop.nodes)

    def get_next_infection_suid(self) -> dict:
        """Get a unique SUID for a new infection."""
        return self._ser_pop.get_next_infection_suid()

    def get_next_individual_suid(self, node_id: int) -> dict:
        """Get a unique SUID for a new individual in the given node."""
        return self._ser_pop.get_next_individual_suid(node_id)

    def write(self, output_file: str | Path = "my_sp_file.dtk") -> None:
        """Write the (possibly modified) population to a file.

        Args:
            output_file (str | Path): Destination file path. Parent directories are
                created if they do not exist.
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._ser_pop.write(str(output_path))

    # -- Inspection --

    def summary(self) -> dict:
        """Return a summary dict with node counts, human counts, etc."""
        from emodpy_malaria.serialization._inspect import summarize
        return summarize(self._ser_pop)

    def find_parameter(self, name: str) -> list[str]:
        """Search for a parameter by name (fuzzy) and return matching paths."""
        from emodpy_malaria.serialization._inspect import find_parameter
        return find_parameter(self._ser_pop, name)

    def __repr__(self) -> str:
        return (
            f"MalariaSerializedPopulation("
            f"file='{self._file_path.name}', "
            f"version={self.version}, "
            f"nodes={self.num_nodes})"
        )
