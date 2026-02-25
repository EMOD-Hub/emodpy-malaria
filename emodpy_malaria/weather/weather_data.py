#!/usr/bin/env python3

"""
Weather data module implementing functionality for working with binary weather files (.bin.json).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Dict, Iterable, List, NoReturn, Tuple, Union


from emodpy_malaria.weather.weather_utils import hash_series, invert_dict, make_path
from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherMetadata, WeatherAttributes, SERIES_BYTE_VALUE_SIZE


class WeatherData:
    """
    Functionality for working with binary weather files (.bin.json).
    """
    def __init__(self, data: np.ndarray, metadata: WeatherMetadata = None):
        """
        Instantiate a weather object from data numpy array and a weather metadata object.

        Args:
            data: Numpy array of unique weather time series, in the order they appear in a .bin file.
                  Shape can either be a single dimension array, or a 2d array having series stored as rows.
                  This means that the number of rows corresponds to the number of unique series and number of
                  columns corresponds to a series length (e.g. 365).
            metadata: (Optional) WeatherMetadata object containing metadata from .bin.json.
        """
        data = self._ensure_data_type(data)
        self._data: np.ndarray = data

        if metadata is not None:
            # If metadata is provided ensure data shape matches metadata info
            self._metadata = metadata
            expected_shape = self._expected_shape()
            if data.shape != expected_shape:
                self._data = data.reshape(expected_shape)
        else:
            # If metadata object is not provided data must be in the correct shape.
            self._metadata = WeatherMetadata(node_ids=list(range(1, data.shape[0] + 1)), series_len=data.shape[1])

        self.validate()

    def __eq__(self, other: WeatherData):
        """Equality operator for WeatherData objects."""
        meta_eq = self.metadata == other.metadata
        data_eq = np.array_equal(self.data, other.data)
        return meta_eq and data_eq

    def _expected_shape(self) -> Tuple[int, int]:
        """Returns the expected shape of data numpy array based on series count and len. """
        return self.metadata.series_unique_count, self.metadata.series_len

    def validate(self):
        """Validate data and metadata relationship."""
        expected_shape = self._expected_shape()
        assert self._data.shape == expected_shape, "Data numpy array shape is not matching metadata counts."

    @property
    def metadata(self) -> WeatherMetadata:
        """Metadata property, exposing weather metadata object."""
        return self._metadata

    @property
    def data(self) -> np.ndarray:
        """Raw data, reshaped in one row per node weather time series."""
        return self._data

    # Import/Export members

    @classmethod
    def from_dict(cls,
                  node_series: Dict[int, Union[np.ndarray[np.float32], List[float]]],
                  same_nodes: Dict[int, List[int]] = None,
                  attributes: WeatherAttributes = None) -> WeatherData:
        """
        Creates a WeatherData object from a dictionary mapping nodes and node weather time series.
        The method identifies unique node weather time series and produces a corresponding node-offset dictionary.

        Args:
            node_series: Dictionary with node ids as keys and weather time series as values (don't have to be unique).
            same_nodes: (Optional) Dictionary, mapping nodes from 'node_series' dictionary to additional nodes
                                   which series are the same. Keys are node ids, values are lists of node ids.
            attributes: (Optional) Attributes used to initiate weather metadata. If not provided, defaults are used.

        Returns:
            WeatherData object.
        """
        # Initialize
        if not isinstance(node_series, Dict) or len(node_series) == 0:
            exception = TypeError if not isinstance(node_series, Dict) else ValueError
            raise exception("The node time series argument must be a non-empty dictionary of node ids and time series.")

        # Check weather time series by converting to an array and validate shape
        try:
            series_values = np.array(list(node_series.values()), dtype=np.float32)
        except ValueError:
            raise ValueError("Time series contains values which are not numbers.")

        if np.any(np.isinf(np.abs(series_values))):
            raise ValueError("Time series contains 'inf' values which indicates failed conversion into np.float32.")

        if len(series_values.shape) != 2:
            raise ValueError("Time series must be a non-empty lists or array of float or integer values. "
                             "All time series must be of the same length.")

        # Check there are no NaN values in node ids
        if any(np.isnan(list(node_series))):
            raise ValueError("Node id list contains 'NaN' values.")

        # Check there are no NaN values in weather time series
        if any(np.isnan(series_values.reshape(-1))):    #
            raise ValueError("Time series contains 'NaN' values.")

        same_nodes = same_nodes or {}

        # Identify unique node weather time series, make sure node ids are int.
        node_series_hashes = {int(n): hash_series(s) for n, s in node_series.items()}       # Create node->hash dict
        unique_nodes = {h: nn[0] for h, nn in invert_dict(node_series_hashes).items()}      # Invert into hash->nodes
        unique_series = [node_series[n] for n in unique_nodes.values()]                     # List unique time series

        # Calculate offset increment per node as time series length x number of bytes per value
        offset_increment = series_values.shape[1] * SERIES_BYTE_VALUE_SIZE
        # Create node->offset dict, for nodes with unique weather time series
        node_offsets = {n: (i * offset_increment) for i, n in enumerate(unique_nodes.values())}
        # Update node->offset dict, add nodes sharing same offsets
        node_offsets.update({n: node_offsets[unique_nodes[h]] for n, h in node_series_hashes.items()})

        # Add other nodes, if specified
        # Invert dict from "unique node"->"list of nodes with that same offset" to "...same..."->"unique node"
        same_nodes = invert_dict(same_nodes, single_value=True)
        node_offsets.update({same: node_offsets[unique] for same, unique in same_nodes.items()})
        # Sort by node, offset
        node_offsets = dict(sorted(node_offsets.items()))

        # Convert the list of weather timeseries into a NumPy array and init WeatherMetadata and WeatherData objects
        data = np.array(unique_series, dtype=np.float32)
        wm = WeatherMetadata(node_ids=node_offsets, series_len=data.shape[1], attributes=attributes)
        wd = WeatherData(data=data, metadata=wm)

        return wd

    def to_dict(self, only_unique_series=False, copy_data: bool = True) -> Dict[int, np.ndarray[np.float32]]:
        """
        Create a node-to-series dictionary from the current object. This method can be used to edit weather data.

        Args:
            only_unique_series: (Optional) A flag controlling whether the output dictionary will contain series for all
                                nodes (if set to true) or only unique series.
            copy_data: (Optional) Flag indicating whether to copy data numpy array to prevent unintentional changes.
        Returns:
            A dictionary with node ids and keys and node weather time series as values.
        """
        data_dict = {}
        node_groups = self.metadata.offset_nodes.values()
        series_list = np.copy(self._data) if copy_data else self._data
        for ng, s in zip(node_groups, series_list):
            ng = ng[:1] if only_unique_series else ng
            data_dict.update(dict(zip(ng, [s] * len(ng))))

        data_dict = dict(sorted(data_dict.items()))

        return data_dict

    @classmethod
    def from_csv(cls, file_path: Union[str, Path], info: DataFrameInfo = None, attributes: WeatherAttributes = None) -> WeatherData:
        """
        Creates a WeatherData object from a csv file. Used for creating or editing weather files.
        The method identifies unique node weather time series and produces a corresponding node-offset dictionary.

        Args:
            file_path: The csv file path from which weather data is loaded (expected columns: node, step, value).
            info: (Optional) Dataframe info object describing dataframe columns and content.
            attributes: (Optional) Attributes used to initiate weather metadata. If not provided, defaults are used.

        Returns:
            WeatherData object.
        """
        assert Path(file_path).is_file(), f"Weather file not found: {file_path}."
        df = pd.read_csv(file_path)
        wd = cls.from_dataframe(df, info=info, attributes=attributes)
        return wd

    def to_csv(self, file_path: Union[str, Path], info: DataFrameInfo = None) -> pd.DataFrame:
        """
        Creates a csv file and stores node ids, time steps and weather node weather time series as separate columns.

        Args:
            file_path: The csv file path into which weather data will be stored.
            info: (Optional) Dataframe info object describing dataframe columns and content.

        Returns:
            Dataframe created as an intermediate object used to save data to a csv file.
        """
        make_path(Path(file_path).parent)
        df = self.to_dataframe(info=info)
        df.to_csv(file_path, index=False)
        return df

    @classmethod
    def from_dataframe(cls,
                       df: pd.DateFrame,
                       info: DataFrameInfo = None,
                       attributes: WeatherAttributes = None) -> WeatherData:
        """
        Creates WeatherData object from the Pandas dataframe. The dataframe is expected to contain
        node ids, time steps and weather node weather time series as separate columns.

        Args:
            df: Dataframe containing nodes and weather time series (expected columns: node, step, value).
            info: (Optional) Dataframe info object describing dataframe columns and content.
            attributes: (Optional) Attributes used to initiate weather metadata. If not provided, defaults are used.

        Returns:
            WeatherData object.
        """
        if not isinstance(df, pd.DataFrame) or len(df) == 0:
            exception = TypeError if not isinstance(df, pd.DataFrame) else ValueError
            raise exception("df argument must be a non-empty pandas DataFrame")

        info = info or DataFrameInfo.detect_columns(df=df)
        nc, sc, vc = [info.node_column, info.step_column, info.value_column]

        # Test for "nan" values in target columns.
        for c in [nc, sc, vc]:
            if df[c].hasnans:
                raise ValueError(f"Column {c} contains 'NaN' values.")

        df = df[[nc, sc, vc]].sort_values(by=[nc, sc])
        df = df[[nc, vc]].set_index(nc)
        node_series = df.groupby(nc).apply(lambda r: r.to_dict('records')).to_dict()
        node_series = {node: [list(d.values())[0] for d in rw] for node, rw in node_series.items()}

        wd = cls.from_dict(node_series=node_series, attributes=attributes)
        return wd

    def to_dataframe(self, info: DataFrameInfo = None) -> pd.DataFrame:
        """
        Creates a dataframe containing node ids, time steps and weather time series as separate columns.

        Args:
            info: (Optional) Dataframe info object describing dataframe columns and content.

        Returns:
            Dataframe containing node ids and weather time series.
        """
        info = info or DataFrameInfo()
        data_dict = self.to_dict(only_unique_series=info.only_unique_series)

        actual_nodes = list(data_dict.keys())
        series_len = self.metadata.series_len
        nodes = np.repeat(actual_nodes, series_len)
        steps = list(range(1, series_len + 1)) * len(actual_nodes)
        values = np.array(list(data_dict.values())).reshape(len(data_dict) * self.metadata.series_len)

        assert len(nodes) == len(steps) == len(values), "Dataframe series lengths don't match"
        # assert all([n == nodes[0] for n in nodes[:series_len] and  == steps[series_len:series_len + 1],
        if len(data_dict) > 1:  # Skip validation in case of a single node.
            assert steps[:series_len] == steps[series_len:series_len * 2], "Steps series is not valid."

        column_series_dict = {info.node_column: nodes, info.step_column: steps, info.value_column: values}
        df = pd.DataFrame(column_series_dict)
        # Set data types
        df[info.node_column] = df[info.node_column].astype(int)
        df[info.step_column] = df[info.step_column].astype(int)
        df[info.value_column] = df[info.value_column].astype(np.float32)
        df.sort_values(by=[info.node_column, info.step_column])
        return df

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> WeatherData:
        """
        Create WeatherData object by reading weather data from binary (.bin) and metadata (.bin.json) files.

        Args:
            file_path: The weather binary (.bin) file path. The metadata file path is constructed by appending ".json".

        Returns:
            WeatherData object.
        """
        file_path = str(file_path)
        wm: WeatherMetadata = WeatherMetadata.from_file(f"{file_path}.json")
        assert Path(file_path).is_file(), f"Data file not found: {file_path}."
        data = np.fromfile(file_path, dtype=np.float32)
        data_len = len(data)
        msg = f"Data length {data_len} doesn't match metadata"
        msg += f" ({wm.series_count} * {wm.series_len} = {wm.total_value_count})"
        assert wm.total_value_count == data_len, msg
        wd = WeatherData(data=data, metadata=wm)
        return wd

    def to_file(self, file_path: Union[str, Path]) -> NoReturn:
        """
        Create weather binary (.bin) and metadata (.json) files, containing weather data and metadata.

        Args:
            file_path: The weather binary (.bin) file path. The metadata file path is constructed by adding ".json".

        Returns:
            None.
        """
        file_path = str(file_path)
        self.validate()
        make_path(Path(file_path).parent)
        self._ensure_data_type(self._data)
        with open(file_path, "wb") as bf:
            self._data.reshape(self.metadata.total_value_count).tofile(bf)

        self._metadata.to_file(f"{file_path}.json")

    @classmethod
    def _ensure_data_type(cls, data: Iterable) -> np.ndarray[np.float32]:
        """
        Ensures node weather time series is of the type compatible with weather binary file format.
        The method validates the data object is iterable and if needed it converts it to the NumPy float32 array.

        Args:
            data: Iterable object containing node weather time series. Usually a list or array of floats values.

        Returns:
            Node weather time series as a NumPy float32 array.
        """
        is_iter_ok = isinstance(data, Iterable) and len(list(data)) > 0
        assert data is not None and is_iter_ok, "Data must have at least one item"
        data = np.array(data, dtype=np.float32)
        return data


class DataFrameInfo:
    """
    The object containing info about dataframe columns and content. Used to pass dataframe info between methods
    working with weather dataframes.
    """
    _variable_values = [str(v.value).lower() for v in WeatherVariable.list()]
    _default_column_candidates = {
        "node": ["nodes", "node", "node_id", "node_ids", "nodeid", "id", "ids"],
        "step": ["steps", "step", "time"],
        "value": ["values", "value", "series", "data"] + _variable_values}

    def __init__(self,
                 node_column: str = None,
                 step_column: str = None,
                 value_column: str = None,
                 only_unique_series: bool = False):
        """
        Initializes dataframe info object. If no info is provided the defaults are used.

        Args:
            node_column: (Optional) Node column name. The default is "nodes".
            step_column: (Optional) Step column name.
            value_column: (Optional) Value column name.
            only_unique_series: (Optional) Flag indicating weather only distinct weather time series are needed.
        """
        self._node_column: str = node_column
        self._step_column: str = step_column
        self._value_column: str = value_column
        self.only_unique_series = only_unique_series
        self._set_defaults()

    def __str__(self) -> str:
        """String representation used to print or debug DataFrameInfo objects."""
        return str(self.__dict__.values())

    def __eq__(self, other: DataFrameInfo):
        """Equality operator for DataFrameInfo objects."""
        if other is None:
            return False

        cols_eq = self._node_column == other.node_column and self._step_column == other.step_column
        cols_eq = cols_eq and self._value_column == other.value_column
        is_eq = cols_eq and self.only_unique_series == other.only_unique_series
        return is_eq

    @property
    def node_column(self):
        return self._node_column

    @property
    def step_column(self):
        return self._step_column

    @property
    def value_column(self):
        return self._value_column

    def _set_defaults(self) -> DataFrameInfo:
        """Create a dataframe info object and initialize variables with defaults."""
        self._node_column = self.node_column or self._default_column_candidates["node"][0]
        self._step_column = self.step_column or self._default_column_candidates["step"][0]
        self._value_column = self.value_column or self._default_column_candidates["value"][0]
        return self

    @classmethod
    def detect_columns(cls, df, column_candidates: Dict[str, List[str]] = None) -> DataFrameInfo:
        """
        Auto-detect required column names (nodes, time-steps and weather time series) for the DataFrameInfo object.

        Args:
            df: The dataframe containing nodes, time-steps and weather time series.
            column_candidates: (Optional) Dictionary of candidate column names to be used instead of defaults.

        Returns:
            DataFrameInfo object with detected column names.
        """
        column_candidates = column_candidates or cls._default_column_candidates

        # Detect columns
        column_types = ["node", "step", "value"]
        columns = [cls._detect_column(df, column_candidates[name]) for name in column_types]
        if not all(columns):
            not_found = [name for name, col in zip(column_types, columns) if col in None]
            raise NameError(f"Unable to detect columns {not_found}.")

        info = DataFrameInfo(*columns)
        return info

    @staticmethod
    def _detect_column(df, column_candidates):
        """
        Detect which of the candidate column names is used in the given dataframe.

        Args:
            df: The dataframe containing nodes, time-steps and weather time series.
            column_candidates: (Optional) Dictionary of candidate column names to be used instead of defaults.

        Returns:
            The detected column name.
        """
        cols = [c for c in df.columns.values if str(c).strip().lower() in column_candidates]
        found_col = None if len(cols) == 0 else cols[0]
        assert found_col is not None and found_col in df.columns.values, "Unable to detect node column."
        return found_col
