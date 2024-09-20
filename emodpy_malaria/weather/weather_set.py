#!/usr/bin/env python3

"""
Weather set module is implementing functionality for working with sets of weather files.
"""

from __future__ import annotations

import pandas as pd

from pathlib import Path
from typing import Dict, List, NoReturn, Tuple, Union

from emodpy_malaria.weather.weather_utils import make_path
from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherAttributes
from emodpy_malaria.weather.weather_data import WeatherData, DataFrameInfo


class WeatherSet:
    """
    Representation of a set of weather files required by EMOD, for all or a subset of weather variables.
    Automate tasks for working with multiple weather files using WeatherData and WeatherMetadata objects.
    WeatherSet contains a dictionary of weather variables to WeatherData and WeatherMetadata objects.
    Supports:
    1. Conversion from/to csv, dataframe (from_csv, to_csv, from_dataframe, to_dataframe)
    2. Conversion from/to EMOD weather files, .bin and .bin.json (from_file, to_file)
    """

    def __init__(self,
                 dir_path: Union[str, Path] = None,
                 file_names: Dict[WeatherVariable, str] = None,
                 weather_columns: Dict[WeatherVariable, str] = None):
        """
        Initializes a WeatherSet object.

        Args:
            dir_path: (Optional) Path to the directory containing weather files.
            file_names: (Optional) Dictionary of weather variables (keys) and file names (values).
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".

        """
        self._dir_path: Union[str, Path] = dir_path
        self._file_names: Dict[WeatherVariable, str] = file_names or {}
        self._weather_columns: Dict[WeatherVariable, str] = weather_columns or {}
        self._weather_dict: Dict[WeatherVariable, WeatherData] = {}

    # Dictionary methods

    def __getitem__(self, weather_variable: WeatherVariable):
        """Getter method for the weather dictionary, to return WeatherData object for the given weather variable."""
        return self._weather_dict[weather_variable]

    def __setitem__(self, weather_variable: WeatherVariable, weather_object: WeatherData):
        """Setter method for the weather dictionary, to set WeatherData object for the given weather variable."""
        self._weather_dict[weather_variable] = weather_object

    def __len__(self):
        """Method to return the number of items in the weather dictionary."""
        return len(self._weather_dict)

    def __str__(self):
        """String representation used to print or debug WeatherSet objects."""
        return str(self.weather_variables)

    def __eq__(self, other: WeatherSet):
        """Equality operator for WeatherSet objects"""
        if self.weather_variables != other.weather_variables:
            return False
        data_eq = [self[v] == other[v] for v in self.weather_variables]
        return all(data_eq)

    def keys(self):
        """Returns the list of WeatherVariables."""
        return self._weather_dict.keys()

    def values(self) -> List[WeatherData]:
        """Returns the list of WeatherData objects."""
        return list(self._weather_dict.values())

    def items(self) -> Dict[WeatherVariable, WeatherData].items:
        """Returns an iterator for weather dictionary items."""
        return self._weather_dict.items()

    # Properties

    @property
    def dir_path(self) -> str:
        """Directory path containing weather files."""
        return str(self._dir_path)

    @property
    def file_names(self) -> Dict[WeatherVariable, str]:
        """Dictionary of weather variables (keys) and weather file names (values)."""
        return self._file_names

    @property
    def attributes(self) -> WeatherAttributes:
        if len(self.weather_variables) > 0:  # if any extract WeatherAttributes (common to all)
            wa = self.values()[0].metadata.attributes
        else:
            wa = None

        return wa

    @property
    def weather_variables(self) -> List[WeatherVariable]:
        """The list of weather variables the weather set covers."""
        return list(self._weather_dict)

    @property
    def weather_columns(self) -> Dict[WeatherVariable, str]:
        """The list of weather columns."""
        return self._weather_columns

    # Export/import

    @classmethod
    def from_dataframe(cls,
                       df: pd.DateFrame,
                       node_column: str = None,
                       step_column: str = None,
                       weather_columns: Dict[WeatherVariable, str] = None,
                       attributes: WeatherAttributes = None) -> WeatherSet:
        """
        Initializes WeatherSet object from a dataframe containing weather time series.
        The dataframe must have node ids, step and weather columns.

        Args:
            df: Dataframe containing weather data.
            node_column: (Optional) Column containing node ids. The default is "nodes".
            step_column: (Optional) Column containing node index for weather time series values. The default is "steps".
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".
            attributes: (Optional) Weather attribute object containing metadata for WeatherMetadata object.

        Returns:
            WeatherSet object.
        """
        assert isinstance(df, pd.DataFrame), f"Unsupported dataframe argument type {type(df)}."
        args = {k: v for k, v in locals().items() if k not in ["cls", "df"]}
        args["data_csv"] = df
        return cls._from_csv_data(**args)

    @classmethod
    def from_csv(cls,
                 file_path: Union[str, Path],
                 node_column: str = None,
                 step_column: str = None,
                 weather_columns: Dict[WeatherVariable, str] = None,
                 attributes: WeatherAttributes = None) -> WeatherSet:
        """
        Initializes WeatherSet object from a dataframe containing weather time series.
        The csv file must have node ids, step and weather columns.

        Args:
            file_path: The csv file path.
            node_column: (Optional) Column containing node ids. The default is "nodes".
            step_column: (Optional) Column containing node index for weather time series values. The default is "steps".
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".
            attributes: (Optional) The weather attribute object containing metadata for WeatherMetadata object.

        Returns:
            WeatherSet object.
        """
        assert Path(file_path).is_file(), f"The csv file not found: {str(file_path)}."
        args = {k: v for k, v in locals().items() if k not in ["cls", "file_path"]}
        args["data_csv"] = str(file_path)
        return cls._from_csv_data(**args)

    @classmethod
    def _from_csv_data(cls,
                       data_csv: Union[str, pd.DataFrame],
                       node_column: str = None,
                       step_column: str = None,
                       weather_columns: Dict[WeatherVariable, str] = None,
                       attributes: WeatherAttributes = None) -> WeatherSet:
        """
         Creates WeatherSet from a csv file or dataframe by instantiating WeatherData object for each weather variable.
         Column arguments are used to interpret input file/dataframe. Weather attribute argument is used for
         instantiating weather metadata objects.

        Args:
            data_csv: Dataframe or a csv file containing weather time series.
            node_column: (Optional) Column containing node ids. The default is "nodes".
            step_column: (Optional) Column containing node index for weather time series values. The default is "steps". The default is "steps".
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".
            attributes: (Optional) The weather attribute object containing metadata for WeatherMetadata object.

        Returns:
            WeatherSet object.
        """
        # Obtain dataframe info objects, to name dataframe columns
        infos, weather_columns = cls._init_dataframe_info_dict(node_column, step_column, weather_columns)
        # Construct the final weather column dictionary (relevant if weather_columns was None or None column names)
        attributes = attributes or WeatherAttributes()
        ws = WeatherSet(weather_columns=weather_columns)
        for v, info in infos.items():
            if isinstance(data_csv, str):
                ws[v] = WeatherData.from_csv(file_path=data_csv, info=info, attributes=attributes)
            elif isinstance(data_csv, pd.DataFrame):
                ws[v] = WeatherData.from_dataframe(df=data_csv, info=info, attributes=attributes)
            else:
                raise TypeError(f"Unsupported argument type {type(data_csv)}. Only string or dataframe are expected.")

        ws.validate()
        return ws

    def to_dataframe(self,
                     node_column: str = None,
                     step_column: str = None,
                     weather_columns: Dict[WeatherVariable, str] = None) -> pd.DataFrame:
        """
        Creates a dataframe containing node ids, time steps and weather columns.

        Args:
            node_column: (Optional) Column containing node ids. The default is "nodes".
            step_column: (Optional) Column containing node index for weather time series values. The default is "steps".
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".
        Returns:
            Dataframe containing node ids and weather time series.
        """
        # If no columns, init keys to filter variables
        weather_columns = weather_columns or {v: None for v in self.weather_variables}
        not_available = [v for v in weather_columns if v.value not in [w.value for w in self.weather_variables]]

        if len(not_available) > 0:
            raise ValueError(f"weather_columns contain unavailable weather variables: {not_available}")

        # Obtain dataframe info objects, to name dataframe columns
        infos, weather_columns = self._init_dataframe_info_dict(node_column, step_column, weather_columns)
        self._weather_columns = weather_columns
        df = None                                   # used to collect all weather columns in a single df
        for v in infos:                             # for each dataframe info (weather variable)
            df2 = self[v].to_dataframe(infos[v])    # get dataframe for current weather variable
            if df is None:                          # if first iteration
                df = df2                            # init outer dataframe
            else:                                   # if 2nd or higher iteration
                col = infos[v].value_column         # take column name
                df[col] = df2[col]                  # add weather column to the outer dataframe

        return df

    def to_csv(self,
               file_path: Union[str, Path],
               node_column: str = None,
               step_column: str = None,
               weather_columns: Dict[WeatherVariable, str] = None) -> pd.DataFrame:
        """
        Creates a csv file containing node ids, time steps and weather columns.

        Args:
            file_path: The path of a csv file to be generated.
            node_column: (Optional) Column containing node ids. The default is "nodes".
            step_column: (Optional) Column containing node index for weather time series values. The default is "steps".
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".

        Returns:
            Dataframe containing node ids and weather time series, used to create the csv file.
        """
        df = self.to_dataframe(node_column, step_column, weather_columns)
        df.to_csv(file_path, index=False)
        return df

    # Save/load DTK files

    def _load(self) -> WeatherSet:
        """Loads weather files based on weather set attributes."""
        assert self.dir_path and Path(self.dir_path).is_dir(), "A valid dir is a required argument."
        assert isinstance(self.file_names, Dict) and len(self.file_names) > 0, "File names dictionary is required."
        for v, n in self.file_names.items():
            bin_path = self._weather_file_path(n)
            self[v] = WeatherData.from_file(bin_path)

        self.validate()

        return self

    def _save(self) -> NoReturn:
        """Saves weather data and metadata into weather files based on weather set attributes."""
        assert self._dir_path, "Directory is a required argument."
        assert self._file_names and len(self._file_names) > 0, "File names are required."

        make_path(self._dir_path)
        for v, wd in self._weather_dict.items():
            bin_path = self._weather_file_path(self._file_names[v])
            wd.to_file(bin_path)
            wd.metadata.to_file(f"{bin_path}.json")

    @classmethod
    def from_files(cls,
                   dir_path: Union[str, Path],
                   prefix: str = "",
                   file_names: Dict[WeatherVariable, str] = None) -> WeatherSet:
        """
        Instantiates WeatherSet from to weather files which paths are determined based on given arguments.

        Args:
            dir_path: Directory path containing weather files.
            prefix: Weather files prefix, e.g. "dtk_15arcmin\_"
            file_names: Dictionary of weather variables (keys) and weather .bin file names (values).

        Returns:
            WeatherSet object.
        """
        WeatherVariable.validate_types(file_names, [str, Path])
        file_names = file_names or cls.select_weather_files(dir_path=dir_path, prefix=prefix)
        ws = WeatherSet(dir_path=dir_path, file_names=file_names)
        ws._load()

        return ws

    def to_files(self,
                 dir_path: Union[str, Path],
                 file_names: Dict[WeatherVariable, str] = None) -> NoReturn:
        """Saves WeatherSet to weather files which paths are determined based on given arguments."""
        file_names = file_names or self.make_file_paths()
        self._dir_path = Path(dir_path)
        self._file_names = file_names
        self._save()

    # Helpers

    @classmethod
    def _init_weather_columns(cls, weather_columns: Dict[WeatherVariable, Union[str, None]] = None
                              ) -> Dict[WeatherVariable, str]:
        """
        Initializes a weather_columns dictionary from defaults or a partially populated weather_columns dictionary.
        The following cases are supported in respect to weather_columns argument:
        - all columns names are specified -> returns unchanged weather_columns
        - some columns names are None: column names are set to WeatherVariable values.
        - weather_columns is  None: all weather columns are set to WeatherVariable values.

        Args:
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".
        Returns:
            Dictionary of weather variables (keys) to weather column names (values).
        """
        WeatherVariable.validate_types(weather_columns, [str, None])
        # Get the list of weather variables - keys from weather_columns or all weather variables
        weather_variables = list(weather_columns) if weather_columns else WeatherVariable.list()
        # If not provided set to empty dict - this will make the following line set WeatherVariable values as defaults.
        weather_columns = weather_columns or {}
        # Transform or construct weather_columns dictionary and fill in missing column names with defaults.
        weather_columns = {v: weather_columns.get(v, None) or v.value for v in weather_variables}
        return weather_columns

    @classmethod
    def _init_dataframe_info_dict(cls,
                                  node_column: str = None,
                                  step_column: str = None,
                                  weather_columns: Dict[WeatherVariable, str] = None
                                  ) -> Tuple[Dict[WeatherVariable, DataFrameInfo], Dict[WeatherVariable, str]]:
        """
        Initializes dataframe info objects containing column names.

        Args:
            node_column: (Optional) Column containing node ids. The default is "nodes".
            step_column: (Optional) Column containing node index for weather time series values. The default is "steps".
            weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                             Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".
        Returns:
            Tuple of two dictionaries mapping weather variables to dataframe info and weather columns.
        """
        weather_columns = cls._init_weather_columns(weather_columns)
        info_dict = {}
        for v in weather_columns:
            info_dict[v] = DataFrameInfo(node_column=node_column,
                                         step_column=step_column,
                                         value_column=weather_columns[v])

        return info_dict, weather_columns

    @classmethod
    def _make_file_templates(cls,
                             prefix: str = "*",
                             suffix: str = "*{}*.bin",
                             weather_variables: List[WeatherVariable] = None,
                             weather_names: Dict[WeatherVariable, str] = None) -> Dict[WeatherVariable, str]:
        """
        Construct file name templates using weather file name prefix/suffix and weather variable names.
        The logic of this method is the same as of "Path.glob" method, with two adjustments, added to make its use more
        convenient for working with weather files:
        - if prefix/suffix are not specified, defaults are used (see method arguments).
        - if suffix doesn't end with ".bin" or "\*", "\*.bin" is added (since, otherwise, no matches can be found).

        Used for two scenarios:
        1. Get expected weather file patsh.
        2. Select weather files from a dir, when exact names are not known, e.g. Path.glob("dtk_\*{tag}\*.bin").

        Args:
            prefix: (Optional) Weather file name prefix, usually a fixed string like "dtk\_".
            suffix: (Optional) Weather file name suffix, usually containing a weather variable name parameter like "\*{tag}\*.bin").
            weather_names: (Optional) Dictionary of weather variables (keys) and custom weather variable names (values).
            weather_variables: (Optional) Weather variables to be used in case custom weather names are not specified.
                In this case lowercase weather variable names are used, for example: AIR_TEMPERATURE -> air_temperature.

        Returns:
            Dictionary of weather variables (keys) and weather file name templates.
                For example, air temperature could be represented as:
                - exact name:   WeatherVariable.AIR_TEMPERATURE: "dtk\_15arcmin\_air\_temperature\_daily.bin" or
                - name pattern: WeatherVariable.AIR_TEMPERATURE: "dtk\_\*air_temperature\*.bin"
        """
        # Validate arguments
        if prefix is None:
            raise ValueError("Prefix cannot be None.")

        if suffix is None:
            raise ValueError("fFile pattern cannot be None.")

        WeatherVariable.validate_types(weather_names, [str])

        is_ok = weather_variables is None or isinstance(weather_variables, List) and len(weather_variables) > 0
        assert is_ok, "If specified weather variables must be a nonempty list."

        # Append *.bin if missing
        if not suffix.endswith(".bin") and not suffix.endswith("*"):
            suffix += "*.bin"

        template = prefix + suffix
        template = template.replace("**", "*")

        # Init default weather name dictionary, if not provided.
        weather_variables = weather_variables or WeatherVariable.list()
        weather_names = weather_names or {v: v.name.lower() for v in weather_variables}

        names = {}
        # Create dictionary of weather variable and file name templates
        for v, t in weather_names.items():
            names[v] = template.format(weather_names[v])

        return names

    @classmethod
    def make_file_paths(cls,
                        dir_path: Union[str, Path] = None,
                        prefix: str = "dtk_15arcmin_",
                        suffix: str = "{}_daily.bin",
                        weather_variables: List[WeatherVariable] = None,
                        weather_names: Dict[WeatherVariable, str] = None) -> Dict[WeatherVariable, str]:
        """
        Construct file paths using the weather directory path, file name prefix/suffix and weather variable names.
        The logic of this method is the same as of "Path.glob" method, with two adjustments, added to make its use more
        convenient for working with weather files:
        - if prefix/suffix are not specified, defaults are used (see method arguments).
        - if suffix doesn't end with ".bin" or "\*", "\*.bin" is added (since, otherwise, no matches can be found).

        Args:
            dir_path: (Optional) Directory path containing weather files.
            prefix: (Optional) Weather file name prefix, usually a fixed string like "dtk\_".
            suffix: (Optional) Weather file name suffix, usually containing a weather variable name parameter like "\*{tag}\*.bin").
            weather_names: (Optional) Dictionary of weather variables (keys) and custom weather variable names (values).
            weather_variables: (Optional) Weather variables to be used in case custom weather names are not specified.
                In this case lowercase weather variable names are used, for example: AIR_TEMPERATURE -> air_temperature.

        Returns:
            Dictionary of weather variables (keys) and weather file paths.
                For example, air temperature could be represented as:
                WeatherVariable.AIR_TEMPERATURE: "dtk_15arcmin_air_temperature_daily.bin"
        """
        names = cls._make_file_templates(prefix=prefix,
                                         suffix=suffix,
                                         weather_names=weather_names,
                                         weather_variables=weather_variables)

        if dir_path is not None:
            names = {v: str(Path(dir_path).joinpath(n)) for v, n in names.items()}

        return names

    @classmethod
    def select_weather_files(cls,
                             dir_path: Union[str, Path],
                             prefix: str = "*",
                             suffix: str = "*{}*.bin",
                             weather_variables: List[WeatherVariable] = None,
                             weather_names: Dict[WeatherVariable, str] = None) -> Dict[WeatherVariable, str]:
        """
        Select a set of weather files using the weather directory path, file name prefix/suffix and weather variable names.
        The logic of this method is the same as of "Path.glob" method, with two adjustments, added to make its use more
        convenient for working with weather files:
        - if prefix/suffix are not specified, defaults are used (see method arguments).
        - if suffix doesn't end with ".bin" or "\*", "\*.bin" is added (since, otherwise, no matches can be found).

        Args:
            dir_path: (Optional) Directory path containing weather files.
            prefix: (Optional) Weather file name prefix, usually a fixed string like "dtk\_".
            suffix: (Optional) Weather file name suffix, usually containing a weather variable name parameter like "\*{tag}\*.bin").
            weather_names: (Optional) Dictionary of weather variables (keys) and custom weather variable names (values).
            weather_variables: (Optional) Weather variables to be used in case custom weather names are not specified.
                In this case lowercase weather variable names are used, for example: AIR_TEMPERATURE -> air_temperature.

         Returns:
             Dictionary of weather variables (keys) and weather file names.
             For example, WeatherVariable.AIR_TEMPERATURE\: "dtk_15arcmin_air_temperature_daily.bin"
         """
        assert dir_path is not None, f"Directory path cannot be None."
        templates = cls._make_file_templates(prefix=prefix,
                                             suffix=suffix,
                                             weather_names=weather_names,
                                             weather_variables=weather_variables)
        names = {}
        # Use name patterns to pick up files via Path.glob().
        for v, pattern in templates.items():
            files = list(Path(dir_path).glob(pattern))
            assert len(files) < 2, f"More than one weather file matches name pattern {pattern}"
            if len(files) == 1:
                names[v] = files[0].name

        return names

    def _weather_file_path(self, file_name: Union[str, Path]) -> Path:
        """Construct a weather file path."""
        return Path(self.dir_path).joinpath(str(file_name))

    def validate(self) -> NoReturn:
        """Validate WeatherSet object."""

        series_len0: Union[int, None] = None
        node_count0: Union[int, None] = None
        if_reference0: Union[str, None] = None
        resolution0: Union[str, None] = None
        years0: Union[str, None] = None

        for v, wd in self._weather_dict.items():
            wm = wd.metadata
            # Validate each weather data and metadata object
            wd.validate()
            wd.metadata.validate()

            # Validate weather objects consistency
            series_len = wm.series_len
            node_count = wm.node_count
            if_reference = wm.id_reference
            resolution = wm.spatial_resolution
            years = wm.data_years
            # total_values = wm.total_value_count

            series_len0 = series_len0 or series_len
            node_count0 = node_count0 or node_count
            if_reference0 = if_reference0 or if_reference
            resolution0 = resolution0 or resolution
            years0 = years0 or years
            # total_values0 = total_values0 or total_values

            file_name = f": {self.file_names[v]}(.json)" if v in self.file_names else ""
            msg = "WeatherSet {} mismatch for " + str(v) + file_name
            assert series_len0 == series_len, msg.format("series_len")
            assert node_count0 == node_count, msg.format("node_count")
            assert if_reference0 == if_reference, msg.format("if_reference")
            assert resolution0 == resolution, msg.format("resolution")
            assert years0 == years, msg.format("data years")
            # assert total_values0 == total_values, msg.format("total_values")

        # Validate that if weather columns are specified they match weather set variables.
        if len(self._weather_columns) > 0:
            for v in WeatherVariable.list():
                both_has = v in self._weather_dict and v in self._weather_columns
                none_has = v not in self._weather_dict and v not in self._weather_columns
                assert both_has or none_has, ""

