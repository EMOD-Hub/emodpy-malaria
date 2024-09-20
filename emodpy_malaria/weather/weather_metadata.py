#!/usr/bin/env python3

"""
Weather metadata module, implementing functionality for working with weather metadata files (.bin.json).
"""

from __future__ import annotations

import numpy as np
import json

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, NoReturn, Union

from emodpy_malaria.weather.weather_utils import invert_dict, make_path, save_json,  validate_str_value

SERIES_BYTE_VALUE_SIZE = 4  # Single series value is stored as 4 bytes = 32b
assert SERIES_BYTE_VALUE_SIZE == np.dtype(np.float32).itemsize, "Unexpected weather time series value size."

# META DEFAULTS
_META_DEFAULT_TOOL = "emodpy_malaria"
_META_DEFAULT_ID_REFERENCE = "Default"
_META_DEFAULT_UNSPECIFIED = "Unspecified"
_META_DEFAULT_AUTHOR = "Institute for Disease Modeling"
_META_DEFAULT_START_DOY = 1
_META_DEFAULT_WEATHER_SCHEMA_V = "2.0"

# META ATTRIBUTE NAMES
# READ-WRITE
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
# READ-ONLY
_META_WEATHER_SCHEMA_V = "WeatherSchemaVersion"
_META_DATA_VALUE_COUNT = "DatavalueCount"
# AUTO-SET
_META_DTK_NODES_COUNT = "NumberDTKNodes"
_META_OFFSET_COUNT = "OffsetEntryCount"
_META_NODE_COUNT = "NodeCount"
_META_DATA_CELL_VALUE_COUNT = "DatavaluePerCell"
# SET BY SERVICE
# _META_WEATHER_CELL_COUNT = "WeatherCellCount"

_META_REQUIRED_ARGS = [_META_ID_REFERENCE]
_META_REQUIRED_CALC = [_META_DATA_VALUE_COUNT]


class WeatherAttributes:
    """
    Weather attributes containing metadata used to construct the "metadata" element and stored in .bin.json file.
    Used to initiate weather metadata object. If no metadata is specified, defaults are used. If metadata dict is
    specified, that dictionary is used as is, without setting any defaults.
    """

    def __init__(self,
                 attributes_dict: Dict[str, Union[str, int, float]] = None,
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
                 schema_version: str = None):
        """
        Initialize the weather attributes object by either passing the metadata dictionary or setting.

        Args:
            attributes_dict:  (Optional) A dictionary containing user specified metadata attributes.
                            Used to initiate weather attributes object. A typical usage is to set metadata attributes
                            including those not required or explicitly implemented by this class. For example, when
                            reading existing metadata file (.bin.json), the dictionary read from the file allows
                            persisting all found attributes, including those explicitly implemented by this class.
                            This dictionary can be used in combination with other __init__ arguments.
            reference:      (Optional) Reference string expected by EMOD as a way to bind weather and demographic files.
            resolution:     (Optional) Spatial weather data resolution.
            provenance:     (Optional) Data provenance describing data source and how it was obtained.
            update_freq:    (Optional) The frequency.
            start_year:     (Optional) Weather data start year. Used to construct years range attribute.
            end_year:       (Optional) Weather data end year. Used to construct years range attribute.
            start_doy:      (Optional) The start day of year. By default, it is set to 1.
            lat_min:        (Optional) Minimal or top latitude of the weather spatial coverage.
            lat_max:        (Optional) Maximum or bottom latitude of the weather spatial coverage.
            lon_min:        (Optional) Minimal or top longitude of the weather spatial coverage.
            lon_max:        (Optional) Maximum or top longitude of the weather spatial coverage.
            tool:           (Optional) The tool used to prepare weather files.
            author:         (Optional) The author of weather files.
            schema_version: (Optional) The EMOD weather file schema version.

        """
        # Init the metadata dictionary to provided dictionary or defaults.
        self._attributes_dict: Dict[str, Union[str, int, float]] = attributes_dict or self.metadata_defaults_dict()

        # If needed, set date attributes based on today's date.
        date_years = f"{start_year}-{end_year}" if start_year is not None and end_year is not None else None

        # Init the metadata object and set arguments. Those that are None are ignored.
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
        }

        # Remove not specified attributes (Nones).
        metadata_args2 = {k: v for k, v in metadata_args.items() if v is not None}
        self._attributes_dict.update(metadata_args2)

        # Set missing required attributes (like IdReference)
        missing_required_defaults = self.required_metadata_defaults_dict(exclude_keys=list(self._attributes_dict.keys()))
        self._attributes_dict.update(missing_required_defaults)

    def __eq__(self, other: WeatherAttributes):
        """Equality operator for WeatherAttributes objects"""
        return self.attributes_dict == other.attributes_dict

    # Getter and setter methods for standard attributes. "snake_case" is for consistency with Python naming convention.

    @property
    def attributes_dict(self) -> Dict[str, Union[str, int, float]]:
        return self._attributes_dict

    @property
    def tool(self) -> str:
        """Tool name used to prepare weather files."""
        return self._attributes_dict.get(_META_TOOL, None)

    @tool.setter
    def tool(self, value: str) -> NoReturn:
        """Set tool name attribute."""
        validate_str_value(value)
        self._attributes_dict[_META_TOOL] = value

    @property
    def date_created(self) -> str:
        """Date weather files are created."""
        return self._attributes_dict.get(_META_DATE_CREATED, None)

    @date_created.setter
    def date_created(self, value: str) -> NoReturn:
        """Set creation date attribute."""
        value = str(value)
        validate_str_value(value)
        # TODO validate date
        self._attributes_dict[_META_DATE_CREATED] = value

    @property
    def author(self) -> str:
        """Author of weather files."""
        return self._attributes_dict.get(_META_AUTHOR, None)

    @author.setter
    def author(self, value: str):
        """Set author attribute."""
        validate_str_value(value)
        self._attributes_dict[_META_AUTHOR] = value

    @property
    def id_reference(self) -> str:
        """Id reference value used to semantically bind weather files."""
        return self._attributes_dict.get(_META_ID_REFERENCE, None)

    @id_reference.setter
    def id_reference(self, value: str):
        """Set id reference attribute."""
        validate_str_value(value)
        self._attributes_dict[_META_ID_REFERENCE] = value

    @property
    def update_resolution(self) -> str:
        """Data update frequency (e.g. monthly, yearly)."""
        return self._attributes_dict.get(_META_UPDATE_FREQUENCY, None)

    @update_resolution.setter
    def update_resolution(self, value: str):
        """Set data update frequency attribute."""
        validate_str_value(value)
        self._attributes_dict[_META_UPDATE_FREQUENCY] = value

    @property
    def data_years(self) -> str:
        """Data years range describing the temporal coverage."""
        return self._attributes_dict.get(_META_DATA_YEARS, None)

    @data_years.setter
    def data_years(self, value: str):
        """Set data years range attribute."""
        validate_str_value(value)
        import re
        assert re.match("20[0-3][0-9]-20[0-3][0-9]", value), "Years range format must be 20YY-20YY"
        self._attributes_dict[_META_DATA_YEARS] = value

    @property
    def provenance(self) -> str:
        """Data provenance, describing the data source and how the data was obtained."""
        return self._attributes_dict.get(_META_PROVENANCE, None)

    @provenance.setter
    def provenance(self, value: str):
        """Set provenance attribute."""
        validate_str_value(value)
        self._attributes_dict[_META_PROVENANCE] = value

    @property
    def spatial_resolution(self) -> str:
        """Weather data Spatial resolution (e.g., 30arcsec or 1km)"""
        return self._attributes_dict.get(_META_SPATIAL_RESOLUTION, None)

    @spatial_resolution.setter
    def spatial_resolution(self, value: str):
        """Set spatial resolution attribute."""
        validate_str_value(value)
        self._attributes_dict[_META_SPATIAL_RESOLUTION] = value

    @classmethod
    def format_create_date(cls, created: datetime) -> str:
        return created.strftime("%Y-%m-%d")

    @classmethod
    def metadata_defaults_dict(cls) -> Dict[str, Union[str, int, float]]:
        """Metadata defaults dictionary."""
        created = datetime.now()
        default_date_years = f"{created.year}-{created.year}"
        metadata = {
            _META_DATE_CREATED: cls.format_create_date(created),
            _META_ID_REFERENCE: _META_DEFAULT_ID_REFERENCE,
            _META_SPATIAL_RESOLUTION: _META_DEFAULT_UNSPECIFIED,
            _META_PROVENANCE: _META_DEFAULT_UNSPECIFIED,
            _META_UPDATE_FREQUENCY: _META_DEFAULT_UNSPECIFIED,
            _META_DATA_YEARS: default_date_years,
            _META_START_DOY: _META_DEFAULT_START_DOY,
            _META_TOOL: _META_DEFAULT_TOOL,
            _META_AUTHOR: _META_DEFAULT_AUTHOR,
            _META_WEATHER_SCHEMA_V: _META_DEFAULT_WEATHER_SCHEMA_V,
        }

        return metadata

    @classmethod
    def required_metadata_defaults_dict(cls, exclude_keys: List[str] = None) -> Dict[str, Union[str, int, float]]:
        """Dictionary of required metadata defaults."""
        exclude_keys = exclude_keys or []
        metadata = {
            k: v for k, v in cls.metadata_defaults_dict().items()
            if k in _META_REQUIRED_ARGS and k not in exclude_keys}
        return metadata

    def update(self, value: Dict[str, Union[int, str]]):
        """Update metadata dictionary."""
        assert isinstance(value, Dict), "Metadata must be a dictionary."
        self._attributes_dict.update(value)

    def validate(self) -> NoReturn:
        """Validate metadata contains requires argument."""
        for a in _META_REQUIRED_ARGS + _META_REQUIRED_CALC:
            assert self._attributes_dict[a] is not None and len(str(a).strip()) > 0, f"{a} metadata attribute is not set."


class WeatherMetadata(WeatherAttributes):
    """
    Weather metadata containing weather data attributes, counts and node offsets.
    Used to initiate WeatherData, expose metadata programmatically and create weather metadata files (.bin.json).
    """

    # REQUIRED_ATTRIBUTES = ["Tool", ]
    def __init__(self,
                 node_ids: Union[List[int], Dict[int, int]],
                 series_len: int = None,
                 attributes: Union[WeatherMetadata, WeatherAttributes, Dict[str, Union[str, int, float]]] = None):
        """
        Initiate WeatherMetadata object.

        Args:
            node_ids: A dictionary with node ids as keys and offsets as values, or just a list of node ids.
                      If node-offset dictionary is provided, node offsets are set per that dictionary.
                      If a list of nodes ids is provided, offsets are calculated based on weather time series length.
            series_len: The length of a weather time series (aka "data value count").
            attributes: Weather attributes, either as an objects or a dictionary.

        """
        if isinstance(attributes, WeatherMetadata) or isinstance(attributes, WeatherAttributes):
            attributes_dict = attributes.attributes_dict
        else:
            attributes_dict = attributes

        super().__init__(attributes_dict=attributes_dict)

        # Set node offsets dictionary based on node_ids argument.
        if isinstance(node_ids, Dict):
            self._node_offsets = node_ids
            series_len = int(series_len or self._expected_series_len())
            self._validate_series_len(series_len)
        else:
            # If node id list is provided, offsets are calculated based on weather time series length.
            self._validate_series_len(series_len)   # if node_ids is a list a valid series_len must be provided.
            self._node_offsets = {
                node_id: series_len * node_ids.index(node_id) * SERIES_BYTE_VALUE_SIZE
                for node_id in sorted(node_ids)
            }

        self._series_len = series_len

        # init
        metadata_count_dict = self._metadata_count_dict

        self.update(metadata_count_dict)
        self.validate()

    def __eq__(self, other: WeatherMetadata):
        """Equality operator for WeatherMetadata objects"""
        attributes_eq = super().__eq__(other)
        nodes_eq = sorted(self.node_offsets) == sorted(other.node_offsets)
        offsets_eq = [self.node_offsets[k] == other.node_offsets[k] for k in self.node_offsets] if nodes_eq else [False]
        return attributes_eq and nodes_eq and offsets_eq

    @property
    def _metadata_count_dict(self):
        node_count = len(self.nodes)
        return {
            _META_OFFSET_COUNT: len(self._node_offsets),
            _META_DTK_NODES_COUNT: node_count,
            _META_NODE_COUNT: node_count,
            _META_DATA_VALUE_COUNT: self._series_len,
            _META_DATA_CELL_VALUE_COUNT: self._series_len,
        }

    @classmethod
    def _validate_series_len(cls, series_len: int):
        if not isinstance(series_len, int) or series_len <= 0:
            raise ValueError("Weather time series length must be an positive integer.")

    def _expected_series_len(self) -> int:
        """Returns expected node weather time series length."""
        if self._node_offsets and len(self._node_offsets) > 0:
            offsets2 = sorted(set(self._node_offsets.values()))[:2]
            expected = int(float(offsets2[1] - offsets2[0]) / 4) if len(offsets2) > 1 else -1
        else:
            expected = -1
        return expected

    def validate(self):
        """Validate metadata object node-related counts. Relies on inherited validation of metadata attributes."""
        super().validate()

        # Validate nodes and offsets
        assert isinstance(self.nodes, Iterable), "node_ids must be iterable"
        assert len(self.nodes) > 0, "node_ids must not be empty"
        assert all(map(lambda i: isinstance(i, int), self.nodes)), "node_ids must be integers"

        # Validate node id and offset range
        # https://github.com/InstituteforDiseaseModeling/DtkTrunk/blob/master/Eradication/Climate.h#L151-L154
        max_uint32 = int("FFFFFFFF", 16)   # max unsigned 32 bit value
        invalid_nodes, invalid_offsets = [], []
        for node_id, offset in self.node_offsets.items():
            if not 0 < node_id <= max_uint32:
                invalid_nodes.append(node_id)

            if not 0 <= offset <= max_uint32:
                invalid_offsets.append(offset)

        if len(invalid_nodes) > 0:
            print(f"Found {len(invalid_nodes)} invalid node ids: {invalid_nodes[:5]}")
            raise ValueError(f"Node values must be integers in (0, {str(max_uint32)}] interval.")

        if len(invalid_offsets) > 0:
            print(f"Found {len(invalid_offsets)} invalid offsets: {invalid_offsets[:5]}")
            raise ValueError(f"Node offset values must be integers in [0, {str(max_uint32)}] interval.")

        assert len(set(self.nodes)) == len(self.nodes), "node_ids must be unique"

        assert len(self.node_offset_str) == self.node_count * 16, "node_offset_str length doesn't match node count. "

        # Validate series_len
        self._validate_series_len(self._series_len)
        if 0 < self._expected_series_len() != self._series_len:
            raise ValueError("Weather time series length doesn't match provided offsets distance.")

    # Operational properties (read-only)
    @property
    def attributes(self) -> WeatherAttributes:
        """Cast back into WeatherAttributes."""
        meta_keys = list(self._metadata_count_dict)
        attributes_dict = {k: v for k, v in self._attributes_dict.items() if k not in meta_keys}
        wa = WeatherAttributes(attributes_dict=attributes_dict)
        return wa

    @property
    def datavalue_count(self) -> int:
        """Number of data values in each weather time series (must be > 0)."""
        return self._series_len

    @property
    def series_len(self) -> int:
        """Number of data values in each timeseries, should be > 0."""
        return self._series_len

    @property
    def series_count(self) -> int:
        """The number of weather time series (expected based on metadata), corresponding to the number of offsets."""
        return len(set(list(self._node_offsets.values())))

    @property
    def series_unique_count(self):
        """The number of unique weather time series (expected based on metadata), based on offsets."""
        return len(self.offset_nodes)

    @property
    def total_value_count(self) -> int:
        """The total count of all values, in all weather time series (expected based on metadata)."""
        return self.series_count * self.series_len

    @property
    def nodes(self) -> List[int]:
        """The list of nodes (node ids) in the node-offset dictionary."""
        return list(self._node_offsets)

    @property
    def node_count(self) -> int:
        """The number of node in the node-offset dictionary."""
        return len(self.nodes)

    @property
    def node_offset_str(self) -> str:
        """The node offset string, as it will appear in the weather metadata file (.bin.json)."""
        return self._convert_offset_dict_to_str(self._node_offsets)

    @property
    def node_offsets(self) -> Dict[int, int]:
        """Node-offset dictionary, mapping node ids (keys) to node offsets (values)."""
        return self._node_offsets

    @property
    def offset_nodes(self) -> Dict[int, List[int]]:
        """The offset-nodes dictionary, grouping nodes (values) by offset (key). Used to find unique series."""
        offset_nodes = invert_dict(self._node_offsets, sort=True)
        return offset_nodes

    # Import/Export members

    def to_file(self, file_path: Union[str, Path]) -> NoReturn:
        """
        Save weather metadata object as weather metadata file (.bin.json).

        Args:
            file_path: The path of the output weather metadata file.

        Returns:
            None
        """
        self.validate()
        # Ensure parent dir exists.
        make_path(Path(file_path).parent)
        # Construct the node offset string.
        offset_str = self._convert_offset_dict_to_str(self._node_offsets)
        # Prepare json object based on metadata and node offset string.
        content = dict(Metadata=self.attributes_dict, NodeOffsets=offset_str)
        # Save json object to a file.
        save_json(content=content, file_path=file_path)

        assert Path(file_path).is_file(), f"Failed to create weather metadata file {file_path}"

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> WeatherMetadata:
        """
        Read weather metadata file into a weather metadata object.
        """
        # Load metadata json file into a json object.
        with open(str(file_path), "rb") as file:
            content = json.load(file)

        # Convert node offset string into a node-offset dictionary
        node_offsets = cls._convert_offset_str_to_dict(content["NodeOffsets"])
        if "Metadata" in content and _META_DATA_VALUE_COUNT in content["Metadata"]:
            series_len = content["Metadata"][_META_DATA_VALUE_COUNT]
        else:
            series_len = None
        # Instantiate the weather metadata object based on node-offset dictionary and metadata attribute dictionary.
        metadata = WeatherMetadata(node_ids=node_offsets, attributes=content["Metadata"], series_len=series_len)

        return metadata

    # Helpers

    @staticmethod
    def _convert_offset_str_to_dict(offset_str: str) -> Dict[int, int]:
        """
        Convert node offset string into a node-offset dictionary.

        Args:
            offset_str: The node offset string.

        Returns:
            The node-offset dictionary, having node ids as keys and offsets as values.
        """
        entry_count = len(offset_str) // 16
        node_offsets = {}
        for i in range(entry_count):
            idx = i * 16
            entry_str = offset_str[idx: idx + 16]
            node_id = int(entry_str[:8], 16)
            offset = int(entry_str[8:16], 16)
            node_offsets[node_id] = offset

        return node_offsets

    @staticmethod
    def _convert_offset_dict_to_str(node_offsets: Dict[int, int]) -> str:
        """
        Convert node-offset dictionary into a string.

        Args:
            node_offsets: The node offset string.

        Returns:
            The node offset string, as it appears in the weather metadata file.
        """
        offset_str = ""
        for node_id, offset in node_offsets.items():
            offset_str += f"{node_id:08x}{offset:08x}"

        return offset_str
