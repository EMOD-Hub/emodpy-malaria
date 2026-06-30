"""Unit tests for emodpy_malaria.serialization._genomes."""

import pytest
import numpy as np

from emodpy_malaria.serialization._genomes import Genome


@pytest.mark.unit
class TestGenome:
    def test_basic_construction(self):
        g = Genome("ACGT", allele_root_id=42)
        assert g.barcode == "ACGT"
        assert g.nucleotides == [0, 1, 2, 3]
        assert g.allele_roots == [42, 42, 42, 42]

    def test_hash_uses_int32_overflow(self):
        g = Genome("ACGTACGTACGTACGTACGTACGT", allele_root_id=1)
        assert isinstance(g.hashcode, int)
        assert isinstance(g.barcode_hashcode, int)
        assert g.hashcode != g.barcode_hashcode

    def test_same_barcode_different_allele_root_gives_different_hashcode(self):
        g1 = Genome("ACGT", allele_root_id=1)
        g2 = Genome("ACGT", allele_root_id=2)
        assert g1.barcode_hashcode == g2.barcode_hashcode
        assert g1.hashcode != g2.hashcode

    def test_to_dtk_dict(self):
        g = Genome("AC", allele_root_id=10)
        d = g.to_dtk_dict()
        assert "m_pInner" in d
        inner = d["m_pInner"]
        assert inner["__class__"] == "ParasiteGenomeInner"
        assert inner["m_NucleotideSequence"] == [0, 1]
        assert inner["m_AlleleRoots"] == [10, 10]
        assert inner["m_HashCode"] == g.hashcode
        assert inner["m_BarcodeHashcode"] == g.barcode_hashcode

    def test_to_dtk_map_entry(self):
        g = Genome("AC", allele_root_id=10)
        entry = g.to_dtk_map_entry()
        assert entry["key"] == g.hashcode
        assert entry["value"]["__class__"] == "ParasiteGenomeInner"

    def test_from_dtk_dict_roundtrip(self):
        original = Genome("ACGTACGT", allele_root_id=42)
        dtk_dict = original.to_dtk_dict()
        reconstructed = Genome.from_dtk_dict(dtk_dict)
        assert reconstructed.barcode == original.barcode
        assert reconstructed.hashcode == original.hashcode
        assert reconstructed.barcode_hashcode == original.barcode_hashcode
        assert reconstructed.nucleotides == original.nucleotides

    def test_nucleotide_to_int(self):
        assert Genome.nucleotide_to_int("A") == 0
        assert Genome.nucleotide_to_int("C") == 1
        assert Genome.nucleotide_to_int("G") == 2
        assert Genome.nucleotide_to_int("T") == 3

    def test_nucleotide_to_int_invalid(self):
        with pytest.raises(ValueError, match="Unknown nucleotide"):
            Genome.nucleotide_to_int("X")

    def test_int_to_nucleotide(self):
        assert Genome.int_to_nucleotide(0) == "A"
        assert Genome.int_to_nucleotide(1) == "C"
        assert Genome.int_to_nucleotide(2) == "G"
        assert Genome.int_to_nucleotide(3) == "T"

    def test_int_to_nucleotide_invalid(self):
        with pytest.raises(ValueError, match="Unknown nucleotide"):
            Genome.int_to_nucleotide(9)

    def test_repr(self):
        g = Genome("AC", allele_root_id=1)
        r = repr(g)
        assert "AC" in r
        assert "Genome" in r

    def test_hash_matches_v1_algorithm(self):
        """Verify hash computation matches the v1 algorithm exactly."""
        barcode = "ACGT"
        allele_root_id = 42

        hash_code = np.int32(17)
        barcode_hash_code = np.int32(17)
        nucleotides = [0, 1, 2, 3]

        for val in nucleotides:
            barcode_hash_code = np.int32(31 * barcode_hash_code + val)
            hash_code = np.int32(31 * hash_code + val)
            hash_code = np.int32(31 * hash_code + allele_root_id)

        g = Genome(barcode, allele_root_id)
        assert g.hashcode == int(hash_code)
        assert g.barcode_hashcode == int(barcode_hash_code)
