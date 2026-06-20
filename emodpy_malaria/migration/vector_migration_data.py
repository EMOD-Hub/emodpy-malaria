from collections import defaultdict
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Optional, Union

import numpy as np

from emodpy.migration.migration_data import (  # noqa: F401
    MigrationData, MALE, FEMALE, SAME_FOR_BOTH_GENDERS, ONE_FOR_EACH_GENDER,
    _author, _compute_gravity_rate, _MIGRATION_TYPE_STRINGS,
)
from emodpy.utils.emod_enum import MigrationType, InterpolationType

logger = logging.getLogger(__name__)

VECTOR_MIGRATION_BY_GENETICS = "VECTOR_MIGRATION_BY_GENETICS"


class VectorMigrationData(MigrationData):
    """Vector migration rate container.

    Extends MigrationData with vector-specific constraints:
    - No age-dependent migration (enforced by EMOD for vectors)
    - InterpolationType forced to PIECEWISE_CONSTANT
    - Supports genetics-based migration via VECTOR_MIGRATION_BY_GENETICS

    Three GenderDataType modes:
    - SAME_FOR_BOTH_GENDERS: 1 layer, same rates for male and female vectors
    - ONE_FOR_EACH_GENDER: 2 layers (male, female)
    - VECTOR_MIGRATION_BY_GENETICS: N layers, one per allele combination.
      The AgesYears metadata field is repurposed to store indices [0, 1, ...]
      into the rate layers, one per allele combination in AlleleCombinations.
    """

    def __init__(self):
        super().__init__()
        self._allele_combinations = None

    @property
    def allele_combinations(self):
        """List of allele combinations for genetics-based migration, or None for standard modes.

        Each entry is a list of allele pairs (list of [allele1, allele2] lists).
        Index 0 is always the default (empty list).
        """
        return self._allele_combinations

    @classmethod
    def from_gravity_model(cls, demographics: object,
                           gravity_params: list[float],
                           female_multiplier: float = None) -> "VectorMigrationData":
        """Generate vector migration rates from a gravity model.

        Uses node population and geodesic distance. Identical to human gravity model
        but restricted to vector migration constraints (no age layers).

        Args:
            demographics: Demographics object with .nodes and .idref
            gravity_params: list of 4 floats [g0, g1, g2, g3].
                rate = g0 * from_pop^g1 * to_pop^g2 * distance_km^g3, capped at 1.0
            female_multiplier: if provided, creates ONE_FOR_EACH_GENDER data where
                female_rate = male_rate * female_multiplier

        Returns:
            VectorMigrationData
        """
        base = MigrationData.from_gravity_model(demographics, gravity_params, female_multiplier)
        data = cls()
        data._idref = base._idref
        data._gender_data_type = base._gender_data_type
        data._layers = base._layers
        return data

    @classmethod
    def from_rates(cls, rates: dict, idref: str = "", female_rates: dict = None) -> "VectorMigrationData":
        """Create vector migration data from explicit rate dictionaries.

        Args:
            rates: dict of {(from_node_id, to_node_id): rate} for male vectors
                (or all vectors if female_rates is None)
            idref: IdReference string
            female_rates: optional dict of {(from_node_id, to_node_id): rate} for female vectors.
                If provided, creates ONE_FOR_EACH_GENDER data.

        Returns:
            VectorMigrationData
        """
        for k, v in rates.items():
            if k[0] == 0 or k[1] == 0:
                raise ValueError("Migration to/from default node (ID=0) is not allowed.")
            if v < 0 or v > 1.0:
                raise ValueError(f"Rate must be in [0.0, 1.0], got {v} for pair {k}.")

        data = cls()
        data._idref = idref
        data._layers = [dict(rates)]

        if female_rates is not None:
            for k, v in female_rates.items():
                if k[0] == 0 or k[1] == 0:
                    raise ValueError("Migration to/from default node (ID=0) is not allowed.")
                if v < 0 or v > 1.0:
                    raise ValueError(f"Rate must be in [0.0, 1.0], got {v} for pair {k}.")
            data._gender_data_type = ONE_FOR_EACH_GENDER
            data._layers = [dict(rates), dict(female_rates)]

        return data

    @classmethod
    def from_genetics(cls, allele_combos_rates: dict, idref: str = "") -> "VectorMigrationData":
        """Create genetics-based vector migration data.

        Each allele combination gets its own rate layer. EMOD matches a vector's genome
        against the allele combinations (most specific first) to select which rate layer
        to use.

        Args:
            allele_combos_rates: dict mapping allele combination tuples to rate dicts.
                Keys are tuples of allele pairs. The empty tuple ``()`` is the default
                (used when no specific combo matches). Example::

                    {
                        (): {(1, 2): 0.01, (2, 1): 0.005},
                        (("a1", "X"),): {(1, 2): 0.02, (2, 1): 0.01},
                        (("a1", "a0"), ("b0", "b1")): {(1, 2): 0.03},
                    }

            idref: IdReference string

        Returns:
            VectorMigrationData with GenderDataType=VECTOR_MIGRATION_BY_GENETICS
        """
        if not allele_combos_rates:
            raise ValueError("allele_combos_rates must not be empty.")

        sorted_keys = sorted(allele_combos_rates.keys(), key=lambda k: (len(k), k))
        if sorted_keys[0] != ():
            raise ValueError("allele_combos_rates must include an empty tuple () as the default combo.")

        layers = []
        allele_combinations = []
        for key in sorted_keys:
            rate_dict = allele_combos_rates[key]
            for k, v in rate_dict.items():
                if k[0] == 0 or k[1] == 0:
                    raise ValueError("Migration to/from default node (ID=0) is not allowed.")
                if v < 0 or v > 1.0:
                    raise ValueError(f"Rate must be in [0.0, 1.0], got {v} for pair {k}.")
            layers.append(dict(rate_dict))
            allele_combinations.append([list(pair) for pair in key])

        data = cls()
        data._idref = idref
        data._gender_data_type = VECTOR_MIGRATION_BY_GENETICS
        # AgesYears is repurposed to store rate layer indices for AlleleCombinations
        data._ages = list(range(len(layers)))
        data._layers = layers
        data._allele_combinations = allele_combinations
        return data

    @classmethod
    def from_migration_file(cls, binary_path: Union[str, Path],
                            metafile: Union[str, Path] = None) -> "VectorMigrationData":
        """Load vector migration data from an existing EMOD binary + JSON metadata file.

        Handles all three GenderDataType modes including VECTOR_MIGRATION_BY_GENETICS
        with AlleleCombinations in metadata.

        Args:
            binary_path: path to the binary migration file
            metafile: path to JSON metadata file (default: binary_path + ".json")

        Returns:
            VectorMigrationData
        """
        binary_path = Path(binary_path).absolute()
        metafile = Path(metafile) if metafile else binary_path.parent / (binary_path.name + ".json")

        if not binary_path.exists():
            raise FileNotFoundError(f"Binary file not found: {binary_path}")
        if not metafile.exists():
            raise FileNotFoundError(f"Metadata file not found: {metafile}")

        with metafile.open("r") as f:
            jason = json.load(f)

        metadata = jason["Metadata"]
        node_count = metadata["NodeCount"]
        datavalue_count = metadata["DatavalueCount"]
        gender_data_type = metadata.get("GenderDataType", SAME_FOR_BOTH_GENDERS)
        # For VECTOR_MIGRATION_BY_GENETICS, AgesYears stores rate layer indices for AlleleCombinations
        ages = metadata.get("AgesYears", [])
        idref = metadata.get("IdReference", "")

        if gender_data_type != VECTOR_MIGRATION_BY_GENETICS and len(ages) > 1:
            raise ValueError(
                "Age-based migration files cannot be used for vector migration. "
                f"File has AgesYears={ages} with GenderDataType={gender_data_type!r}. "
                "Vector migration does not support age-dependent rates."
            )

        node_offsets_str = jason["NodeOffsets"]
        offsets = {}
        for i in range(node_count):
            base = 16 * i
            node_id = int(node_offsets_str[base:base + 8], 16)
            offset = int(node_offsets_str[base + 8:base + 16], 16)
            offsets[node_id] = offset

        if gender_data_type == VECTOR_MIGRATION_BY_GENETICS:
            num_genders = 1
        elif gender_data_type == ONE_FOR_EACH_GENDER:
            num_genders = 2
        else:
            num_genders = 1

        num_ages = len(ages) if ages else 1
        age_data_size = node_count * datavalue_count * 12
        gender_data_size = num_ages * age_data_size

        offsets.pop(0, None)

        layers = []
        with binary_path.open("rb") as f:
            for gender in range(num_genders):
                for age_idx in range(num_ages):
                    layer = {}
                    for node_id, node_offset in offsets.items():
                        file_offset = gender * gender_data_size + age_idx * age_data_size + node_offset
                        f.seek(file_offset)
                        destinations = np.fromfile(f, dtype=np.uint32, count=datavalue_count)
                        rates = np.fromfile(f, dtype=np.float64, count=datavalue_count)
                        for dest, rate in zip(destinations, rates):
                            if rate > 0 and dest > 0:
                                layer[(node_id, int(dest))] = float(rate)
                    layers.append(layer)

        data = cls()
        data._idref = idref
        data._gender_data_type = gender_data_type
        data._ages = ages
        data._layers = layers
        data._user_notes = metadata.get("USER_NOTES", None)

        if gender_data_type == VECTOR_MIGRATION_BY_GENETICS:
            allele_combos = metadata.get("AlleleCombinations", None)
            if allele_combos is None:
                raise ValueError(
                    "VECTOR_MIGRATION_BY_GENETICS requires AlleleCombinations in metadata, "
                    "but none was found."
                )
            if len(ages) != len(allele_combos):
                raise ValueError(
                    f"AgesYears has {len(ages)} entries but AlleleCombinations has "
                    f"{len(allele_combos)} entries. These must match (one age index per "
                    f"allele combination)."
                )
            data._allele_combinations = allele_combos

        return data

    def apply_modifier(self, ages, modifier_fn):
        """Not supported for vector migration — vectors do not have age-dependent rates."""
        raise NotImplementedError("Vector migration does not support age-dependent rates. "
                                  "Use from_rates() or from_genetics() to set per-layer rates.")

    def to_migration_file(self, path: Union[str, Path],
                          migration_type: Union[MigrationType, str] = MigrationType.LOCAL,
                          interpolation_type: object = None,
                          value_limit: int = 100,
                          user_notes: Optional[str] = None) -> Path:
        """Write vector migration data to EMOD binary format with JSON metadata sidecar.

        InterpolationType is always PIECEWISE_CONSTANT for vector migration (the
        interpolation_type parameter is ignored).

        For VECTOR_MIGRATION_BY_GENETICS mode, writes AlleleCombinations to metadata
        and uses AgesYears as allele combo indices.

        Args:
            path: output path for the binary file (metadata written to path + ".json")
            migration_type: MigrationType enum or string. Default LOCAL.
            interpolation_type: ignored — always PIECEWISE_CONSTANT for vectors
            value_limit: max destinations per source node (default 100)
            user_notes: free-text description stored in metadata as USER_NOTES

        Returns:
            Path to binary file
        """
        if not isinstance(migration_type, MigrationType):
            try:
                migration_type = MigrationType(migration_type.upper())
            except ValueError:
                raise ValueError(f"Invalid migration_type '{migration_type}'. "
                                 f"Valid options: {list(MigrationType)}")

        path = Path(path).absolute()
        metafile = path.parent / (path.name + ".json")

        if 0 in self.node_ids:
            raise ValueError("Migration data must not contain default node (ID=0). "
                             "Cannot write migration to/from the default node.")

        mig_type_str = _MIGRATION_TYPE_STRINGS[migration_type]

        source_nodes = set()
        for layer in self._layers:
            source_nodes |= set(from_id for from_id, _ in layer)
        source_nodes = sorted(source_nodes)

        max_dests = 0
        for layer in self._layers:
            dests_per_node = defaultdict(int)
            for from_id, _ in layer:
                dests_per_node[from_id] += 1
            if dests_per_node:
                max_dests = max(max_dests, max(dests_per_node.values()))
        actual_dvc = min(max_dests, value_limit)
        if actual_dvc == 0:
            actual_dvc = 1

        offsets = {node: 12 * i * actual_dvc for i, node in enumerate(source_nodes)}
        node_offsets_str = ''.join(f"{node:08x}{offsets[node]:08x}" for node in source_nodes)

        metadata = {
            "Metadata": {
                "Author": _author(),
                "DateCreated": f"{datetime.now():%a %b %d %Y %H:%M:%S}",
                "Tool": "emodpy-malaria",
                "IdReference": self._idref,
                "MigrationType": mig_type_str,
                "NodeCount": len(source_nodes),
                "DatavalueCount": actual_dvc,
                "GenderDataType": self._gender_data_type,
                "InterpolationType": str(InterpolationType.PIECEWISE_CONSTANT),
            },
            "NodeOffsets": node_offsets_str
        }

        if self._gender_data_type == VECTOR_MIGRATION_BY_GENETICS:
            if self._allele_combinations is None:
                raise ValueError(
                    "VECTOR_MIGRATION_BY_GENETICS requires allele_combinations data, "
                    "but none is set."
                )
            if len(self._allele_combinations) != len(self._layers):
                raise ValueError(
                    f"allele_combinations has {len(self._allele_combinations)} entries but "
                    f"there are {len(self._layers)} rate layers. These must match."
                )
            # AgesYears is repurposed to store rate layer indices for AlleleCombinations
            metadata["Metadata"]["AgesYears"] = list(range(len(self._layers)))
            metadata["Metadata"]["AlleleCombinations"] = self._allele_combinations
        elif self._gender_data_type == ONE_FOR_EACH_GENDER:
            pass
        else:
            pass

        notes = user_notes or self._user_notes
        if notes is not None:
            metadata["Metadata"]["USER_NOTES"] = notes

        with metafile.open("w") as f:
            json.dump(metadata, f, indent=4, separators=(",", ": "))

        with path.open("wb") as f:
            for layer in self._layers:
                rates_by_source = defaultdict(list)
                for (from_id, to_id), rate in layer.items():
                    rates_by_source[from_id].append((to_id, rate))

                for node in source_nodes:
                    pairs = rates_by_source.get(node, [])
                    pairs.sort(key=lambda x: x[1], reverse=True)
                    if len(pairs) > actual_dvc:
                        pairs = pairs[:actual_dvc]
                    pairs.sort(key=lambda x: x[1])

                    destinations = np.zeros(actual_dvc, dtype=np.uint32)
                    rates = np.zeros(actual_dvc, dtype=np.float64)
                    for i, (dest, rate) in enumerate(pairs):
                        destinations[i] = dest
                        rates[i] = rate

                    destinations.tofile(f)
                    rates.tofile(f)

        return path
