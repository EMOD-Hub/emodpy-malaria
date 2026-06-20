"""Weather metadata classes for EMOD ``.bin.json`` files.

Wraps [emod_api.weather.weather.Metadata](https://emod.idmod.org/emod-api/autoapi/emod_api/weather/weather/) (``BaseMetadata``) for core
node-offset computation and ``.bin.json`` parsing, and extends it with:

* [WeatherAttributes](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/weather/weather_metadata/) — rich metadata (provenance, spatial resolution,
  lat/lon bounds, schema version, etc.).
* [WeatherMetadata](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/weather/weather_metadata/) — adds shared-offset support (deduplication) and
  the extended attribute set to the base metadata.
"""

import json
import numpy as np

from datetime import datetime
from pathlib import Path
from typing import Union

from emod_api.weather.weather import Metadata as BaseMetadata

from emodpy_malaria.weather.weather_utils import invert_dict, make_path, save_json, validate_str_value

SERIES_BYTE_VALUE_SIZE = 4
assert SERIES_BYTE_VALUE_SIZE == np.dtype(np.float32).itemsize

# Metadata key constants
_META_TOOL = "Tool"
_META_DATE_CREATED = "DateCreated"
_META_AUTHOR = "Author"
_META_ID_REFERENCE = "IdReference"
_META_UPDATE_FREQUENCY = "UpdateResolution"
_META_DATA_YEARS = "OriginalDataYears"
_META_START_DOY = "StartDayOfYear"
_META_PROVENANCE = "DataProvenance"
_META_SPATIAL_RESOLUTION = "Resolution"
_META_LAT_MAX = "UpperLatitude"
_META_LON_MIN = "LeftLongitude"
_META_LAT_MIN = "BottomLatitude"
_META_LON_MAX = "RightLongitude"
_META_WEATHER_SCHEMA_V = "WeatherSchemaVersion"
_META_NOTES = "Notes"
_META_DATA_VALUE_COUNT = "DatavalueCount"
_META_DTK_NODES_COUNT = "NumberDTKNodes"
_META_OFFSET_COUNT = "OffsetEntryCount"
_META_NODE_COUNT = "NodeCount"
_META_DATA_CELL_VALUE_COUNT = "DatavaluePerCell"
_META_WEATHER_CELL_COUNT = "WeatherCellCount"

# Defaults
_META_DEFAULT_TOOL = "emodpy_malaria"
_META_DEFAULT_ID_REFERENCE = "Default"
_META_DEFAULT_UNSPECIFIED = "Unspecified"
_META_DEFAULT_AUTHOR = "Institute for Disease Modeling"
_META_DEFAULT_START_DOY = 1
_META_DEFAULT_WEATHER_SCHEMA_V = "2.0"

_META_REQUIRED_ARGS = [_META_ID_REFERENCE]
_META_REQUIRED_CALC = [_META_DATA_VALUE_COUNT]


class WeatherAttributes:
    """Metadata attributes for EMOD weather files.

    Manages the key/value pairs stored in the ``"Metadata"`` section of a
    ``.bin.json`` file.  Provides sensible defaults when no explicit values
    are given.
    """

    def __init__(self,
                 attributes_dict: dict[str, Union[str, int, float]] = None,
                 reference: str = None,
                 resolution: str = None,
                 provenance: str = None,
                 update_freq: str = None,
                 start_year: int = None,
                 end_year: int = None,
                 start_doy: int = None,
                 lat_min: float = None,
                 lat_max: float = None,
                 lon_min: float = None,
                 lon_max: float = None,
                 tool: str = None,
                 author: str = None,
                 schema_version: str = None,
                 notes: str = None):
        self._attributes_dict: dict[str, Union[str, int, float]] = (
            attributes_dict or self.metadata_defaults_dict()
        )

        date_years = f"{start_year}-{end_year}" if start_year is not None and end_year is not None else None

        metadata_args = {
            _META_ID_REFERENCE: reference,
            _META_SPATIAL_RESOLUTION: resolution,
            _META_PROVENANCE: provenance,
            _META_UPDATE_FREQUENCY: update_freq,
            _META_DATA_YEARS: date_years,
            _META_START_DOY: start_doy,
            _META_LAT_MIN: lat_min,
            _META_LAT_MAX: lat_max,
            _META_LON_MIN: lon_min,
            _META_LON_MAX: lon_max,
            _META_TOOL: tool,
            _META_AUTHOR: author,
            _META_WEATHER_SCHEMA_V: schema_version,
            _META_NOTES: notes,
        }

        metadata_args = {k: v for k, v in metadata_args.items() if v is not None}
        self._attributes_dict.update(metadata_args)

        missing = self.required_metadata_defaults_dict(exclude_keys=list(self._attributes_dict.keys()))
        self._attributes_dict.update(missing)

    def __eq__(self, other):
        if not isinstance(other, WeatherAttributes):
            return NotImplemented
        return self.attributes_dict == other.attributes_dict

    @property
    def attributes_dict(self) -> dict[str, Union[str, int, float]]:
        return self._attributes_dict

    @property
    def tool(self) -> str | None:
        return self._attributes_dict.get(_META_TOOL)

    @tool.setter
    def tool(self, value: str) -> None:
        validate_str_value(value)
        self._attributes_dict[_META_TOOL] = value

    @property
    def date_created(self) -> str | None:
        return self._attributes_dict.get(_META_DATE_CREATED)

    @date_created.setter
    def date_created(self, value: str) -> None:
        validate_str_value(str(value))
        self._attributes_dict[_META_DATE_CREATED] = str(value)

    @property
    def author(self) -> str | None:
        return self._attributes_dict.get(_META_AUTHOR)

    @author.setter
    def author(self, value: str) -> None:
        validate_str_value(value)
        self._attributes_dict[_META_AUTHOR] = value

    @property
    def id_reference(self) -> str | None:
        return self._attributes_dict.get(_META_ID_REFERENCE)

    @id_reference.setter
    def id_reference(self, value: str) -> None:
        validate_str_value(value)
        self._attributes_dict[_META_ID_REFERENCE] = value

    @property
    def update_resolution(self) -> str | None:
        return self._attributes_dict.get(_META_UPDATE_FREQUENCY)

    @update_resolution.setter
    def update_resolution(self, value: str) -> None:
        validate_str_value(value)
        self._attributes_dict[_META_UPDATE_FREQUENCY] = value

    @property
    def data_years(self) -> str | None:
        return self._attributes_dict.get(_META_DATA_YEARS)

    @data_years.setter
    def data_years(self, value: str) -> None:
        validate_str_value(value)
        import re
        if not re.match(r"20[0-3][0-9]-20[0-3][0-9]", value):
            raise ValueError("Years range format must be 20YY-20YY")
        self._attributes_dict[_META_DATA_YEARS] = value

    @property
    def provenance(self) -> str | None:
        return self._attributes_dict.get(_META_PROVENANCE)

    @provenance.setter
    def provenance(self, value: str) -> None:
        validate_str_value(value)
        self._attributes_dict[_META_PROVENANCE] = value

    @property
    def spatial_resolution(self) -> str | None:
        return self._attributes_dict.get(_META_SPATIAL_RESOLUTION)

    @spatial_resolution.setter
    def spatial_resolution(self, value: str) -> None:
        validate_str_value(value)
        self._attributes_dict[_META_SPATIAL_RESOLUTION] = value

    @property
    def notes(self) -> str | None:
        return self._attributes_dict.get(_META_NOTES)

    @notes.setter
    def notes(self, value: str) -> None:
        validate_str_value(value)
        self._attributes_dict[_META_NOTES] = value

    @classmethod
    def format_create_date(cls, created: datetime) -> str:
        return created.strftime("%Y-%m-%d")

    @classmethod
    def metadata_defaults_dict(cls) -> dict[str, Union[str, int, float]]:
        created = datetime.now()
        return {
            _META_DATE_CREATED: cls.format_create_date(created),
            _META_ID_REFERENCE: _META_DEFAULT_ID_REFERENCE,
            _META_SPATIAL_RESOLUTION: _META_DEFAULT_UNSPECIFIED,
            _META_PROVENANCE: _META_DEFAULT_UNSPECIFIED,
            _META_UPDATE_FREQUENCY: _META_DEFAULT_UNSPECIFIED,
            _META_DATA_YEARS: f"{created.year}-{created.year}",
            _META_START_DOY: _META_DEFAULT_START_DOY,
            _META_TOOL: _META_DEFAULT_TOOL,
            _META_AUTHOR: _META_DEFAULT_AUTHOR,
            _META_WEATHER_SCHEMA_V: _META_DEFAULT_WEATHER_SCHEMA_V,
        }

    @classmethod
    def required_metadata_defaults_dict(cls, exclude_keys: list[str] = None) -> dict[str, Union[str, int, float]]:
        exclude_keys = exclude_keys or []
        return {
            k: v for k, v in cls.metadata_defaults_dict().items()
            if k in _META_REQUIRED_ARGS and k not in exclude_keys
        }

    def update(self, value: dict[str, Union[int, str]]) -> None:
        if not isinstance(value, dict):
            raise TypeError("Metadata must be a dictionary.")
        self._attributes_dict.update(value)

    def validate(self) -> None:
        for a in _META_REQUIRED_ARGS + _META_REQUIRED_CALC:
            val = self._attributes_dict.get(a)
            if val is None or len(str(val).strip()) == 0:
                raise ValueError(f"Required metadata attribute {a!r} is not set.")


class WeatherMetadata(WeatherAttributes):
    """Weather metadata with node offsets and count fields.

    Wraps [emod_api.weather.weather.Metadata](https://emod.idmod.org/emod-api/autoapi/emod_api/weather/weather/) for core node-offset
    computation and basic ``.bin.json`` parsing, extending it with rich
    metadata attributes and shared-offset (deduplication) support.
    """

    def __init__(self,
                 node_ids: Union[list[int], dict[int, int]],
                 series_len: int = None,
                 attributes: Union["WeatherMetadata", WeatherAttributes,
                                   dict[str, Union[str, int, float]]] = None):
        if isinstance(attributes, (WeatherMetadata, WeatherAttributes)):
            attributes_dict = attributes.attributes_dict
        else:
            attributes_dict = attributes

        super().__init__(attributes_dict=attributes_dict)

        if isinstance(node_ids, dict):
            # Shared-offset case — store the dict directly
            self._node_offsets = node_ids
            series_len = int(series_len or self._expected_series_len())
            self._validate_series_len(series_len)
        else:
            # Simple list — delegate offset calculation to emod-api Metadata
            self._validate_series_len(series_len)
            base = BaseMetadata(list(node_ids), series_len)
            self._node_offsets = dict(base.nodes)

        self._series_len = series_len
        self.update(self._metadata_count_dict)
        self.validate()

    def __eq__(self, other):
        if not isinstance(other, WeatherMetadata):
            return NotImplemented
        return (super().__eq__(other)
                and sorted(self.node_offsets) == sorted(other.node_offsets)
                and all(self.node_offsets[k] == other.node_offsets[k]
                        for k in self.node_offsets))

    def to_base_metadata(self) -> BaseMetadata:
        """Create an [emod_api.weather.weather.Metadata](https://emod.idmod.org/emod-api/autoapi/emod_api/weather/weather/) instance.

        Useful for interoperability with code that expects the emod-api
        ``Metadata`` object.  Note: shared offsets are expanded — each
        node gets its own sequential offset in the returned object.
        """
        return BaseMetadata(
            node_ids=self.nodes,
            datavalue_count=self._series_len,
            author=self.author,
            provenance=self.provenance,
            reference=self.id_reference,
            frequency=self.update_resolution,
        )

    @property
    def _metadata_count_dict(self):
        node_count = len(self.nodes)
        return {
            _META_OFFSET_COUNT: len(self._node_offsets),
            _META_DTK_NODES_COUNT: node_count,
            _META_NODE_COUNT: node_count,
            _META_WEATHER_CELL_COUNT: node_count,
            _META_DATA_VALUE_COUNT: self._series_len,
            _META_DATA_CELL_VALUE_COUNT: self._series_len,
        }

    @classmethod
    def _validate_series_len(cls, series_len: int) -> None:
        if not isinstance(series_len, int) or series_len <= 0:
            raise ValueError("Weather time series length must be a positive integer.")

    def _expected_series_len(self) -> int:
        if self._node_offsets and len(self._node_offsets) > 0:
            offsets = sorted(set(self._node_offsets.values()))[:2]
            if len(offsets) > 1:
                return int((offsets[1] - offsets[0]) / SERIES_BYTE_VALUE_SIZE)
        return -1

    def validate(self) -> None:
        super().validate()

        if not self.nodes:
            raise ValueError("node_ids must not be empty.")
        if not all(isinstance(i, int) for i in self.nodes):
            raise TypeError("node_ids must be integers.")

        max_uint32 = 0xFFFFFFFF
        invalid_nodes = [n for n in self.nodes if not (0 < n <= max_uint32)]
        if invalid_nodes:
            raise ValueError(
                f"Node IDs must be in (0, {max_uint32}]. "
                f"Invalid: {invalid_nodes[:5]}"
            )

        invalid_offsets = [
            o for o in self.node_offsets.values()
            if not (0 <= o <= max_uint32)
        ]
        if invalid_offsets:
            raise ValueError(
                f"Offsets must be in [0, {max_uint32}]. "
                f"Invalid: {invalid_offsets[:5]}"
            )

        if len(set(self.nodes)) != len(self.nodes):
            raise ValueError("node_ids must be unique.")

        if len(self.node_offset_str) != self.node_count * 16:
            raise ValueError("node_offset_str length doesn't match node count.")

        self._validate_series_len(self._series_len)
        expected = self._expected_series_len()
        if 0 < expected != self._series_len:
            raise ValueError("Time series length doesn't match offset distances.")

    @property
    def attributes(self) -> WeatherAttributes:
        meta_keys = list(self._metadata_count_dict)
        attributes_dict = {
            k: v for k, v in self._attributes_dict.items()
            if k not in meta_keys
        }
        return WeatherAttributes(attributes_dict=attributes_dict)

    @property
    def datavalue_count(self) -> int:
        return self._series_len

    @property
    def series_len(self) -> int:
        return self._series_len

    @property
    def series_count(self) -> int:
        return len(set(self._node_offsets.values()))

    @property
    def series_unique_count(self) -> int:
        return len(self.offset_nodes)

    @property
    def total_value_count(self) -> int:
        return self.series_count * self.series_len

    @property
    def nodes(self) -> list[int]:
        return list(self._node_offsets)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def node_offset_str(self) -> str:
        return self._convert_offset_dict_to_str(self._node_offsets)

    @property
    def node_offsets(self) -> dict[int, int]:
        return self._node_offsets

    @property
    def offset_nodes(self) -> dict[int, list[int]]:
        return invert_dict(self._node_offsets, sort=True)

    def to_file(self, file_path: Union[str, Path]) -> None:
        """Write the rich ``.bin.json`` metadata file.

        Produces a superset of the format written by
        [emod_api.weather.weather.Metadata.write_file()](https://emod.idmod.org/emod-api/autoapi/emod_api/weather/weather/), including
        additional attributes like ``Tool``, ``WeatherSchemaVersion``,
        ``Resolution``, etc.
        """
        self.validate()
        make_path(Path(file_path).parent)
        offset_str = self._convert_offset_dict_to_str(self._node_offsets)
        content = dict(Metadata=self.attributes_dict, NodeOffsets=offset_str)
        save_json(content=content, file_path=file_path)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "WeatherMetadata":
        """Read a ``.bin.json`` file.

        Uses [emod_api.weather.weather.Metadata.from_file()](https://emod.idmod.org/emod-api/autoapi/emod_api/weather/weather/) for core
        parsing (node offsets, datavalue count), then augments with any
        additional attributes present in the file.
        """
        base = BaseMetadata.from_file(str(file_path))

        with open(str(file_path), "rb") as f:
            content = json.load(f)
        raw_meta = content.get("Metadata", {})

        return WeatherMetadata(
            node_ids=dict(base.nodes),
            series_len=base.datavalue_count,
            attributes=raw_meta,
        )

    @staticmethod
    def _convert_offset_str_to_dict(offset_str: str) -> dict[int, int]:
        entry_count = len(offset_str) // 16
        node_offsets = {}
        for i in range(entry_count):
            idx = i * 16
            entry = offset_str[idx: idx + 16]
            node_offsets[int(entry[:8], 16)] = int(entry[8:16], 16)
        return node_offsets

    @staticmethod
    def _convert_offset_dict_to_str(node_offsets: dict[int, int]) -> str:
        return "".join(f"{node_id:08x}{offset:08x}"
                       for node_id, offset in node_offsets.items())
