"""Weather data classes for reading/writing EMOD binary weather files (``.bin``).

Wraps :class:`emod_api.weather.weather.Weather` (``BaseWeather``) for core
binary file I/O, extending it with:

* Shared-offset support (deduplication of identical time series).
* DataFrame import/export.
* Rich metadata attributes via :class:`~emodpy_malaria.weather.weather_metadata.WeatherMetadata`.

:class:`DataFrameInfo` is a helper for detecting or specifying DataFrame
column names when converting between tabular and binary formats.
"""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Union

from emod_api.weather.weather import Weather as BaseWeather

from emodpy_malaria.weather.weather_utils import hash_series, invert_dict, make_path
from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherMetadata, WeatherAttributes, SERIES_BYTE_VALUE_SIZE


class WeatherData:
    """Binary weather data and its metadata for a single weather variable."""

    def __init__(self, data: np.ndarray, metadata: WeatherMetadata = None):
        """Create from a NumPy array of unique time series.

        Args:
            data: float32 array. Shape ``(n_unique_series, series_len)`` or
                  a flat 1-D array that will be reshaped using *metadata*.
            metadata: If omitted, auto-generated with node IDs 1..N.
        """
        data = self._ensure_data_type(data)
        self._data: np.ndarray = data

        if metadata is not None:
            self._metadata = metadata
            expected = self._expected_shape()
            if data.shape != expected:
                self._data = data.reshape(expected)
        else:
            self._metadata = WeatherMetadata(
                node_ids=list(range(1, data.shape[0] + 1)),
                series_len=data.shape[1],
            )

        self.validate()

    def __eq__(self, other):
        if not isinstance(other, WeatherData):
            return NotImplemented
        return self.metadata == other.metadata and np.array_equal(self.data, other.data)

    def _expected_shape(self) -> tuple[int, int]:
        return self.metadata.series_unique_count, self.metadata.series_len

    def validate(self) -> None:
        expected = self._expected_shape()
        if self._data.shape != expected:
            raise ValueError(
                f"Data shape {self._data.shape} doesn't match metadata "
                f"(expected {expected})."
            )

    @property
    def metadata(self) -> WeatherMetadata:
        return self._metadata

    @property
    def data(self) -> np.ndarray:
        return self._data

    def to_base_weather(self) -> BaseWeather:
        """Create an :class:`emod_api.weather.weather.Weather` instance.

        Useful for interoperability with code that expects the emod-api
        ``Weather`` object.  Note: shared offsets are expanded — each node
        gets its own copy of the data in the returned object.
        """
        expanded = self.to_dict()
        node_ids = sorted(expanded.keys())
        data = np.array([expanded[n] for n in node_ids], dtype=np.float32)
        base_meta = self._metadata.to_base_metadata()
        return BaseWeather(
            node_ids=node_ids,
            datavalue_count=self._metadata.series_len,
            author=base_meta.author,
            provenance=base_meta.provenance,
            reference=base_meta.id_reference,
            data=data,
        )

    @classmethod
    def from_base_weather(cls, base: BaseWeather,
                          attributes: WeatherAttributes = None) -> "WeatherData":
        """Create from an :class:`emod_api.weather.weather.Weather` instance."""
        node_series = {
            node_id: base.nodes[node_id].data
            for node_id in base.node_ids
        }
        return cls.from_dict(node_series=node_series, attributes=attributes)

    # ------------------------------------------------------------------ #
    # Import / Export
    # ------------------------------------------------------------------ #

    @classmethod
    def from_dict(cls,
                  node_series: dict[int, Union[np.ndarray, list[float]]],
                  same_nodes: dict[int, list[int]] = None,
                  attributes: WeatherAttributes = None) -> "WeatherData":
        """Create from a ``{node_id: time_series}`` dictionary.

        Identifies unique series and builds a compact binary representation.

        Args:
            node_series: Node ID to time series mapping.
            same_nodes: Optional mapping of nodes in *node_series* to
                additional node IDs that share the same data.
            attributes: Optional metadata attributes.
        """
        if not isinstance(node_series, dict) or len(node_series) == 0:
            exc = TypeError if not isinstance(node_series, dict) else ValueError
            raise exc("node_series must be a non-empty dictionary.")

        try:
            series_values = np.array(list(node_series.values()), dtype=np.float32)
        except (ValueError, TypeError):
            raise ValueError("Time series contains values that cannot be converted to float32.")

        if np.any(np.isinf(series_values)):
            raise ValueError("Time series contains infinite values.")
        if len(series_values.shape) != 2:
            raise ValueError("All time series must be non-empty lists of equal length.")
        if any(np.isnan(list(node_series))):
            raise ValueError("Node ID list contains NaN values.")
        if np.any(np.isnan(series_values)):
            raise ValueError("Time series contains NaN values.")

        same_nodes = same_nodes or {}

        node_series_hashes = {int(n): hash_series(s) for n, s in node_series.items()}
        unique_nodes = {h: nn[0] for h, nn in invert_dict(node_series_hashes).items()}
        unique_series = [node_series[n] for n in unique_nodes.values()]

        offset_increment = series_values.shape[1] * SERIES_BYTE_VALUE_SIZE
        node_offsets = {n: (i * offset_increment) for i, n in enumerate(unique_nodes.values())}
        node_offsets.update({n: node_offsets[unique_nodes[h]] for n, h in node_series_hashes.items()})

        same_inverted = invert_dict(same_nodes, single_value=True)
        node_offsets.update({same: node_offsets[unique] for same, unique in same_inverted.items()})
        node_offsets = dict(sorted(node_offsets.items()))

        data = np.array(unique_series, dtype=np.float32)
        wm = WeatherMetadata(node_ids=node_offsets, series_len=data.shape[1], attributes=attributes)
        return WeatherData(data=data, metadata=wm)

    def to_dict(self, only_unique_series: bool = False, copy_data: bool = True) -> dict[int, np.ndarray]:
        """Export as ``{node_id: series}`` dictionary."""
        data_dict = {}
        node_groups = self.metadata.offset_nodes.values()
        series_list = np.copy(self._data) if copy_data else self._data
        for ng, s in zip(node_groups, series_list):
            nodes = ng[:1] if only_unique_series else ng
            data_dict.update(dict(zip(nodes, [s] * len(nodes))))
        return dict(sorted(data_dict.items()))

    @classmethod
    def from_csv(cls, file_path: Union[str, Path],
                 info: "DataFrameInfo" = None,
                 attributes: WeatherAttributes = None) -> "WeatherData":
        """Load from a CSV with node, step, and value columns."""
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Weather CSV not found: {file_path}")
        df = pd.read_csv(file_path)
        return cls.from_dataframe(df, info=info, attributes=attributes)

    def to_csv(self, file_path: Union[str, Path], info: "DataFrameInfo" = None) -> pd.DataFrame:
        """Write to CSV and return the DataFrame."""
        make_path(Path(file_path).parent)
        df = self.to_dataframe(info=info)
        df.to_csv(file_path, index=False)
        return df

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame,
                       info: "DataFrameInfo" = None,
                       attributes: WeatherAttributes = None) -> "WeatherData":
        """Create from a pandas DataFrame with node, step, and value columns."""
        if not isinstance(df, pd.DataFrame) or len(df) == 0:
            exc = TypeError if not isinstance(df, pd.DataFrame) else ValueError
            raise exc("df must be a non-empty pandas DataFrame.")

        info = info or DataFrameInfo.detect_columns(df=df)
        nc, sc, vc = info.node_column, info.step_column, info.value_column

        for c in [nc, sc, vc]:
            if df[c].hasnans:
                raise ValueError(f"Column {c!r} contains NaN values.")

        df = df[[nc, sc, vc]].sort_values(by=[nc, sc])
        df = df[[nc, vc]].set_index(nc)
        node_series = df.groupby(nc).apply(lambda r: r.to_dict("records"), include_groups=False).to_dict()
        node_series = {node: [list(d.values())[0] for d in rw] for node, rw in node_series.items()}

        return cls.from_dict(node_series=node_series, attributes=attributes)

    def to_dataframe(self, info: "DataFrameInfo" = None) -> pd.DataFrame:
        """Convert to a DataFrame with node, step, and value columns."""
        info = info or DataFrameInfo()
        data_dict = self.to_dict(only_unique_series=info.only_unique_series)

        actual_nodes = list(data_dict.keys())
        sl = self.metadata.series_len
        nodes = np.repeat(actual_nodes, sl)
        steps = list(range(1, sl + 1)) * len(actual_nodes)
        values = np.array(list(data_dict.values())).reshape(len(data_dict) * sl)

        df = pd.DataFrame({
            info.node_column: nodes,
            info.step_column: steps,
            info.value_column: values,
        })
        df[info.node_column] = df[info.node_column].astype(int)
        df[info.step_column] = df[info.step_column].astype(int)
        df[info.value_column] = df[info.value_column].astype(np.float32)
        df.sort_values(by=[info.node_column, info.step_column], inplace=True)
        return df

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "WeatherData":
        """Read from a ``.bin`` / ``.bin.json`` file pair."""
        file_path = str(file_path)
        wm = WeatherMetadata.from_file(f"{file_path}.json")
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        data = np.fromfile(file_path, dtype=np.float32)
        if wm.total_value_count != len(data):
            raise ValueError(
                f"Data length {len(data)} doesn't match metadata "
                f"({wm.series_count} * {wm.series_len} = {wm.total_value_count})."
            )
        return WeatherData(data=data, metadata=wm)

    def to_file(self, file_path: Union[str, Path]) -> None:
        """Write ``.bin`` and ``.bin.json`` files."""
        file_path = str(file_path)
        self.validate()
        make_path(Path(file_path).parent)
        self._ensure_data_type(self._data)
        with open(file_path, "wb") as bf:
            self._data.reshape(self.metadata.total_value_count).tofile(bf)
        self._metadata.to_file(f"{file_path}.json")

    @classmethod
    def _ensure_data_type(cls, data) -> np.ndarray:
        if data is None or not hasattr(data, "__len__") or len(data) == 0:
            raise ValueError("Data must be a non-empty iterable.")
        return np.array(data, dtype=np.float32)


class DataFrameInfo:
    """Column name configuration for weather DataFrames."""

    _variable_values = [str(v.value).lower() for v in WeatherVariable.list()]
    _default_column_candidates = {
        "node": ["nodes", "node", "node_id", "node_ids", "nodeid", "id", "ids"],
        "step": ["steps", "step", "time"],
        "value": ["values", "value", "series", "data"] + _variable_values,
    }

    def __init__(self,
                 node_column: str = None,
                 step_column: str = None,
                 value_column: str = None,
                 only_unique_series: bool = False):
        self._node_column = node_column
        self._step_column = step_column
        self._value_column = value_column
        self.only_unique_series = only_unique_series
        self._set_defaults()

    def __eq__(self, other):
        if not isinstance(other, DataFrameInfo):
            return NotImplemented
        return (self._node_column == other.node_column
                and self._step_column == other.step_column
                and self._value_column == other.value_column
                and self.only_unique_series == other.only_unique_series)

    @property
    def node_column(self):
        return self._node_column

    @property
    def step_column(self):
        return self._step_column

    @property
    def value_column(self):
        return self._value_column

    def _set_defaults(self) -> None:
        self._node_column = self._node_column or self._default_column_candidates["node"][0]
        self._step_column = self._step_column or self._default_column_candidates["step"][0]
        self._value_column = self._value_column or self._default_column_candidates["value"][0]

    @classmethod
    def detect_columns(cls, df: pd.DataFrame,
                       column_candidates: dict[str, list[str]] = None) -> "DataFrameInfo":
        """Auto-detect node, step, and value column names from a DataFrame."""
        column_candidates = column_candidates or cls._default_column_candidates
        column_types = ["node", "step", "value"]
        columns = [cls._detect_column(df, column_candidates[name]) for name in column_types]
        not_found = [name for name, col in zip(column_types, columns) if col is None]
        if not_found:
            raise NameError(f"Unable to detect columns: {not_found}")
        return DataFrameInfo(*columns)

    @staticmethod
    def _detect_column(df: pd.DataFrame, column_candidates: list[str]) -> str | None:
        cols = [c for c in df.columns if str(c).strip().lower() in column_candidates]
        return cols[0] if cols else None
