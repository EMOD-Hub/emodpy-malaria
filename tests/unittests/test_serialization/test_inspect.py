"""Unit tests for emodpy_malaria.serialization._inspect."""

import json
import struct
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from emodpy_malaria.serialization._inspect import (
    read_header,
    count_humans,
    count_infections,
    list_node_ids,
)


class MockAttrDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


def _make_mock_ser_pop(nodes_data):
    """Create a mock SerializedPopulation with the given node data.

    nodes_data: list of dicts with keys like
        {"externalId": 1, "individualHumans": [...], "m_vectorpopulations": [...]}
    """
    nodes = []
    for nd in nodes_data:
        node = MockAttrDict(nd)
        node["individualHumans"] = nd.get("individualHumans", [])
        node["m_vectorpopulations"] = nd.get("m_vectorpopulations", [])
        nodes.append(node)

    ser_pop = MagicMock()
    ser_pop.nodes = nodes
    return ser_pop


def _make_human(suid_id, num_infections=0, infected=False, age=3650.0):
    return MockAttrDict({
        "suid": MockAttrDict({"id": suid_id}),
        "infections": [{"suid": {"id": i}} for i in range(num_infections)],
        "m_is_infected": infected,
        "m_age": age,
        "m_female_gametocytes": 0,
        "m_male_gametocytes": 0,
    })


class TestCountHumans:
    def test_all_nodes(self):
        ser_pop = _make_mock_ser_pop([
            {"externalId": 1, "individualHumans": [_make_human(1), _make_human(2)]},
            {"externalId": 2, "individualHumans": [_make_human(3)]},
        ])
        assert count_humans(ser_pop) == 3

    def test_specific_node(self):
        ser_pop = _make_mock_ser_pop([
            {"externalId": 1, "individualHumans": [_make_human(1), _make_human(2)]},
            {"externalId": 2, "individualHumans": [_make_human(3)]},
        ])
        assert count_humans(ser_pop, node_index=0) == 2
        assert count_humans(ser_pop, node_index=1) == 1

    def test_empty(self):
        ser_pop = _make_mock_ser_pop([
            {"externalId": 1, "individualHumans": []},
        ])
        assert count_humans(ser_pop) == 0


class TestCountInfections:
    def test_counts_across_nodes(self):
        ser_pop = _make_mock_ser_pop([
            {"externalId": 1, "individualHumans": [
                _make_human(1, num_infections=2),
                _make_human(2, num_infections=1),
            ]},
            {"externalId": 2, "individualHumans": [
                _make_human(3, num_infections=3),
            ]},
        ])
        assert count_infections(ser_pop) == 6

    def test_specific_node(self):
        ser_pop = _make_mock_ser_pop([
            {"externalId": 1, "individualHumans": [_make_human(1, num_infections=2)]},
            {"externalId": 2, "individualHumans": [_make_human(2, num_infections=5)]},
        ])
        assert count_infections(ser_pop, node_index=1) == 5


class TestListNodeIds:
    def test_returns_external_ids(self):
        ser_pop = _make_mock_ser_pop([
            {"externalId": 100, "individualHumans": []},
            {"externalId": 200, "individualHumans": []},
            {"externalId": 300, "individualHumans": []},
        ])
        assert list_node_ids(ser_pop) == [100, 200, 300]


class TestReadHeader:
    def test_reads_v6_header(self, tmp_path):
        header_json = {
            "version": 6,
            "author": "IDM",
            "tool": "DTK",
            "date": "Mon Jan 01 00:00:00 2025",
            "sim_compression": "LZ4",
        }
        header_bytes = json.dumps(header_json).encode()
        header_size_str = f"{len(header_bytes):012d}".encode()

        dtk_file = tmp_path / "test.dtk"
        with open(dtk_file, "wb") as f:
            f.write(b"IDTK")
            f.write(header_size_str)
            f.write(header_bytes)

        result = read_header(dtk_file)
        assert result["version"] == 6
        assert result["author"] == "IDM"
        assert result["sim_compression"] == "LZ4"

    def test_invalid_magic_raises(self, tmp_path):
        dtk_file = tmp_path / "bad.dtk"
        with open(dtk_file, "wb") as f:
            f.write(b"NOPE")
            f.write(b"000000000010")
            f.write(b'{"version":1}')

        with pytest.raises(ValueError, match="incorrect magic"):
            read_header(dtk_file)
