"""Parasite genome representation and replacement in serialized populations."""

from __future__ import annotations

import logging
import warnings
from typing import Callable

import numpy as np

from emod_api.serialization.serialized_population import SerializedPopulation

logger = logging.getLogger(__name__)

_NUCLEOTIDE_MAP = {"A": 0, "C": 1, "G": 2, "T": 3}
_NUCLEOTIDE_REVERSE = {0: "A", 1: "C", 2: "G", 3: "T"}

_HASH_SEED = np.int32(17)
_HASH_MULTIPLIER = np.int32(31)


class Genome:
    """Represents a single parasite genome with barcode-to-DTK-dict conversion.

    Args:
        barcode (str): Nucleotide string (characters A/C/G/T).
        allele_root_id (int): Root ID for allele tracking. Typically the
            individual's SUID or -999 for vectors.
    """

    def __init__(self, barcode: str, allele_root_id: int) -> None:
        self._barcode = barcode
        self._nucleotides: list[int] = []
        self._allele_roots: list[int] = []
        self._hash_code = np.int32(_HASH_SEED)
        self._barcode_hash_code = np.int32(_HASH_SEED)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            for ch in barcode:
                val = self.nucleotide_to_int(ch)
                self._nucleotides.append(val)
                self._allele_roots.append(allele_root_id)
                self._barcode_hash_code = np.int32(
                    _HASH_MULTIPLIER * self._barcode_hash_code + val
                )
                self._hash_code = np.int32(
                    _HASH_MULTIPLIER * self._hash_code + val
                )
                self._hash_code = np.int32(
                    _HASH_MULTIPLIER * self._hash_code + allele_root_id
                )

    @property
    def barcode(self) -> str:
        return self._barcode

    @property
    def hashcode(self) -> int:
        return int(self._hash_code)

    @property
    def barcode_hashcode(self) -> int:
        return int(self._barcode_hash_code)

    @property
    def nucleotides(self) -> list[int]:
        return list(self._nucleotides)

    @property
    def allele_roots(self) -> list[int]:
        return list(self._allele_roots)

    def to_dtk_dict(self) -> dict:
        """Convert to DTK genome dict format (``m_pInner`` structure)."""
        return {
            "m_pInner": {
                "__class__": "ParasiteGenomeInner",
                "m_HashCode": self.hashcode,
                "m_BarcodeHashcode": self.barcode_hashcode,
                "m_NucleotideSequence": self._nucleotides,
                "m_AlleleRoots": self._allele_roots,
            }
        }

    def to_dtk_map_entry(self) -> dict:
        """Convert to DTK genome map entry format (key/value pair)."""
        return {
            "key": self.hashcode,
            "value": self.to_dtk_dict()["m_pInner"],
        }

    @staticmethod
    def from_dtk_dict(dtk_dict: dict) -> Genome:
        """Construct a Genome from a DTK genome dict.

        Args:
            dtk_dict (dict): A dict with ``m_pInner`` key containing genome data.

        Returns:
            Genome instance with matching barcode and hash codes.
        """
        inner = dtk_dict["m_pInner"]
        nucleotides = inner["m_NucleotideSequence"]
        allele_roots = inner["m_AlleleRoots"]

        barcode = "".join(Genome.int_to_nucleotide(n) for n in nucleotides)
        allele_root_id = allele_roots[0] if allele_roots else 0

        genome = Genome(barcode, allele_root_id)
        return genome

    @staticmethod
    def nucleotide_to_int(ch: str) -> int:
        """Convert a single nucleotide character to its integer encoding."""
        if ch not in _NUCLEOTIDE_MAP:
            raise ValueError(
                f"Unknown nucleotide character {ch!r}. "
                f"Valid: {list(_NUCLEOTIDE_MAP.keys())}"
            )
        return _NUCLEOTIDE_MAP[ch]

    @staticmethod
    def int_to_nucleotide(val: int) -> str:
        """Convert an integer encoding back to a nucleotide character."""
        if val not in _NUCLEOTIDE_REVERSE:
            raise ValueError(
                f"Unknown nucleotide value {val!r}. Valid: {list(_NUCLEOTIDE_REVERSE.keys())}"
            )
        return _NUCLEOTIDE_REVERSE[val]

    def __repr__(self) -> str:
        return f"Genome(barcode={self._barcode!r}, hashcode={self.hashcode})"


def _get_next_genome(
    next_barcode_fn: Callable[[], str],
    allele_root_id: int,
    genome_map: list,
    cache: dict[str, Genome],
) -> dict:
    """Generate or retrieve a cached genome, adding new ones to the map."""
    barcode_str = next_barcode_fn()
    key = f"{barcode_str}-{allele_root_id}"

    if key not in cache:
        genome = Genome(barcode_str, allele_root_id)
        cache[key] = genome
        genome_map.append(genome.to_dtk_map_entry())

    return cache[key].to_dtk_dict()


def replace_genomes(
    ser_pop: SerializedPopulation,
    next_barcode_fn: Callable[[], str],
) -> int:
    """Replace all parasite genomes in humans and vectors (in-place).

    Clears the simulation-level ParasiteGenomeMap and rebuilds it with new
    genomes generated by calling ``next_barcode_fn()`` for each infection.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.
        next_barcode_fn (Callable[[], str]): Callable returning a barcode string each time
            it is called.

    Returns:
        Total number of genomes replaced.

    Raises:
        ValueError: If a generated barcode has a different length than the
            existing barcode at that position.
    """
    if next_barcode_fn is None:
        raise ValueError("next_barcode_fn must not be None")

    genome_map = ser_pop.dtk.simulation["ParasiteGenetics"]["m_ParasiteGenomeMap"]
    genome_map.clear()
    cache: dict[str, Genome] = {}
    count = 0

    for node in ser_pop.nodes:
        for person in node["individualHumans"]:
            person_id = person["suid"]["id"]
            for infection in person["infections"]:
                existing = infection["infection_strain"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"]
                new_genome = _get_next_genome(next_barcode_fn, person_id, genome_map, cache)
                if len(new_genome["m_pInner"]["m_NucleotideSequence"]) != len(existing):
                    raise ValueError(
                        f"New barcode length {len(new_genome['m_pInner']['m_NucleotideSequence'])} "
                        f"does not match existing length {len(existing)}"
                    )
                infection["infection_strain"]["m_Genome"] = new_genome
                count += 1

        for vector_pop in node["m_vectorpopulations"]:
            for vector in vector_pop["AdultQueues"]["collection"]:
                for oocyst in vector["m_OocystCohorts"]:
                    existing = oocyst["m_MaleGametocyteGenome"]["m_pInner"]["m_NucleotideSequence"]
                    new_genome = _get_next_genome(next_barcode_fn, -999, genome_map, cache)
                    if len(new_genome["m_pInner"]["m_NucleotideSequence"]) != len(existing):
                        raise ValueError("New barcode length does not match existing oocyst male genome length")
                    oocyst["m_MaleGametocyteGenome"] = new_genome

                    existing = oocyst["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"]
                    new_genome = _get_next_genome(next_barcode_fn, -999, genome_map, cache)
                    if len(new_genome["m_pInner"]["m_NucleotideSequence"]) != len(existing):
                        raise ValueError("New barcode length does not match existing oocyst female genome length")
                    oocyst["m_pStrainIdentity"]["m_Genome"] = new_genome
                    count += 2

                for sporo in vector["m_SporozoiteCohorts"]:
                    existing = sporo["m_MaleGametocyteGenome"]["m_pInner"]["m_NucleotideSequence"]
                    new_genome = _get_next_genome(next_barcode_fn, -999, genome_map, cache)
                    if len(new_genome["m_pInner"]["m_NucleotideSequence"]) != len(existing):
                        raise ValueError("New barcode length does not match existing sporozoite male genome length")
                    sporo["m_MaleGametocyteGenome"] = new_genome

                    existing = sporo["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"]
                    new_genome = _get_next_genome(next_barcode_fn, -999, genome_map, cache)
                    if len(new_genome["m_pInner"]["m_NucleotideSequence"]) != len(existing):
                        raise ValueError("New barcode length does not match existing sporozoite female genome length")
                    sporo["m_pStrainIdentity"]["m_Genome"] = new_genome
                    count += 2

    return count


def get_all_barcodes(ser_pop: SerializedPopulation) -> list[str]:
    """Extract all unique barcode strings from the population's genome map.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.

    Returns:
        List of unique barcode strings.
    """
    genome_map = ser_pop.dtk.simulation["ParasiteGenetics"]["m_ParasiteGenomeMap"]
    barcodes = []
    for entry in genome_map:
        nucleotides = entry["value"]["m_NucleotideSequence"]
        barcode = "".join(Genome.int_to_nucleotide(n) for n in nucleotides)
        barcodes.append(barcode)
    return barcodes


def get_infection_barcodes(
    ser_pop: SerializedPopulation,
    *,
    node_index: int | None = None,
) -> list[dict]:
    """Extract barcode information for each infection in the population.

    Args:
        ser_pop (SerializedPopulation): A loaded SerializedPopulation.
        node_index (int ): If provided, inspect only this node.

    Returns:
        List of dicts with keys ``node_id``, ``individual_id``,
        ``infection_index``, ``barcode``, ``hashcode``.
    """
    results = []
    nodes = ser_pop.nodes
    indices = [node_index] if node_index is not None else range(len(nodes))

    for idx in indices:
        node = nodes[idx]
        node_id = node.externalId
        for person in node["individualHumans"]:
            person_id = person["suid"]["id"]
            for inf_idx, infection in enumerate(person["infections"]):
                inner = infection["infection_strain"]["m_Genome"]["m_pInner"]
                nucleotides = inner["m_NucleotideSequence"]
                barcode = "".join(Genome.int_to_nucleotide(n) for n in nucleotides)
                results.append({
                    "node_id": node_id,
                    "individual_id": person_id,
                    "infection_index": inf_idx,
                    "barcode": barcode,
                    "hashcode": inner["m_HashCode"],
                })

    return results
