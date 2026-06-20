"""Multi-variable weather file set management.

:class:`WeatherSet` wraps a dictionary of
``WeatherVariable -> WeatherData`` and supports bulk I/O: read/write all
four EMOD weather file pairs at once, or convert to/from a single CSV or
DataFrame containing all variables.
"""

import pandas as pd

from pathlib import Path
from typing import Union

from emodpy_malaria.weather.weather_utils import make_path
from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherAttributes
from emodpy_malaria.weather.weather_data import WeatherData, DataFrameInfo


class WeatherSet:
    """A set of weather files for all (or a subset of) EMOD weather variables."""

    def __init__(self,
                 dir_path: Union[str, Path] = None,
                 file_names: dict[WeatherVariable, str] = None,
                 weather_columns: dict[WeatherVariable, str] = None):
        self._dir_path: Union[str, Path] = dir_path
        self._file_names: dict[WeatherVariable, str] = file_names or {}
        self._weather_columns: dict[WeatherVariable, str] = weather_columns or {}
        self._weather_dict: dict[WeatherVariable, WeatherData] = {}

    def __getitem__(self, weather_variable: WeatherVariable):
        return self._weather_dict[weather_variable]

    def __setitem__(self, weather_variable: WeatherVariable, weather_object: WeatherData):
        self._weather_dict[weather_variable] = weather_object

    def __len__(self):
        return len(self._weather_dict)

    def __str__(self):
        return str(self.weather_variables)

    def __eq__(self, other):
        if not isinstance(other, WeatherSet):
            return NotImplemented
        if self.weather_variables != other.weather_variables:
            return False
        return all(self[v] == other[v] for v in self.weather_variables)

    def keys(self):
        return self._weather_dict.keys()

    def values(self) -> list[WeatherData]:
        return list(self._weather_dict.values())

    def items(self):
        return self._weather_dict.items()

    @property
    def dir_path(self) -> str:
        return str(self._dir_path)

    @property
    def file_names(self) -> dict[WeatherVariable, str]:
        return self._file_names

    @property
    def attributes(self) -> WeatherAttributes | None:
        if self.weather_variables:
            return self.values()[0].metadata.attributes
        return None

    @property
    def node_ids(self) -> list[int]:
        if self.weather_variables:
            return self.values()[0].metadata.nodes
        return []

    @property
    def id_reference(self) -> str | None:
        if self.weather_variables:
            return self.values()[0].metadata.id_reference
        return None

    @id_reference.setter
    def id_reference(self, value: str) -> None:
        for wd in self.values():
            wd.metadata.id_reference = value

    @property
    def update_resolution(self) -> str | None:
        if self.weather_variables:
            return self.values()[0].metadata.update_resolution
        return None

    @update_resolution.setter
    def update_resolution(self, value: str) -> None:
        for wd in self.values():
            wd.metadata.update_resolution = value

    @property
    def notes(self) -> str | None:
        if self.weather_variables:
            return self.values()[0].metadata.notes
        return None

    @notes.setter
    def notes(self, value: str) -> None:
        for wd in self.values():
            wd.metadata.notes = value

    @property
    def weather_variables(self) -> list[WeatherVariable]:
        return list(self._weather_dict)

    @property
    def weather_columns(self) -> dict[WeatherVariable, str]:
        return self._weather_columns

    # ------------------------------------------------------------------ #
    # CSV / DataFrame I/O
    # ------------------------------------------------------------------ #

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame,
                       node_column: str = None,
                       step_column: str = None,
                       weather_columns: dict[WeatherVariable, str] = None,
                       attributes: WeatherAttributes = None,
                       notes: str = None) -> "WeatherSet":
        """Create from a DataFrame containing all weather variables as columns.

        Args:
            df: DataFrame with node, step, and weather variable columns.
            node_column: Column name for node IDs.
            step_column: Column name for time steps.
            weather_columns: ``{WeatherVariable: column_name}`` mapping.
            attributes: Optional metadata attributes.
            notes: Free-text note stored in the weather file metadata.
                Use this to record where the original data came from and
                how it was processed.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected DataFrame, got {type(df)}.")
        return cls._from_csv_data(
            data_csv=df, node_column=node_column, step_column=step_column,
            weather_columns=weather_columns, attributes=attributes, notes=notes,
        )

    @classmethod
    def from_csv(cls, file_path: Union[str, Path],
                 node_column: str = None,
                 step_column: str = None,
                 weather_columns: dict[WeatherVariable, str] = None,
                 attributes: WeatherAttributes = None,
                 notes: str = None) -> "WeatherSet":
        """Create from a CSV file containing all weather variables.

        Args:
            file_path: Path to the CSV file.
            node_column: Column name for node IDs.
            step_column: Column name for time steps.
            weather_columns: ``{WeatherVariable: column_name}`` mapping.
            attributes: Optional metadata attributes.
            notes: Free-text note stored in the weather file metadata.
                Use this to record where the original data came from and
                how it was processed.
        """
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        return cls._from_csv_data(
            data_csv=str(file_path), node_column=node_column, step_column=step_column,
            weather_columns=weather_columns, attributes=attributes, notes=notes,
        )

    @classmethod
    def _from_csv_data(cls,
                       data_csv: Union[str, pd.DataFrame],
                       node_column: str = None,
                       step_column: str = None,
                       weather_columns: dict[WeatherVariable, str] = None,
                       attributes: WeatherAttributes = None,
                       notes: str = None) -> "WeatherSet":
        infos, weather_columns = cls._init_dataframe_info_dict(node_column, step_column, weather_columns)
        attributes = attributes or WeatherAttributes()
        if notes is not None:
            attributes.notes = notes
        ws = WeatherSet(weather_columns=weather_columns)
        for v, info in infos.items():
            if isinstance(data_csv, str):
                ws[v] = WeatherData.from_csv(file_path=data_csv, info=info, attributes=attributes)
            elif isinstance(data_csv, pd.DataFrame):
                ws[v] = WeatherData.from_dataframe(df=data_csv, info=info, attributes=attributes)
            else:
                raise TypeError(f"Unsupported data type {type(data_csv)}.")
        ws.validate()
        return ws

    def to_dataframe(self,
                     node_column: str = None,
                     step_column: str = None,
                     weather_columns: dict[WeatherVariable, str] = None) -> pd.DataFrame:
        """Export all variables to a single DataFrame."""
        weather_columns = weather_columns or {v: None for v in self.weather_variables}
        not_available = [v for v in weather_columns if v not in self.weather_variables]
        if not_available:
            raise ValueError(f"Requested unavailable weather variables: {not_available}")

        infos, weather_columns = self._init_dataframe_info_dict(node_column, step_column, weather_columns)
        self._weather_columns = weather_columns
        df = None
        for v in infos:
            df2 = self[v].to_dataframe(infos[v])
            if df is None:
                df = df2
            else:
                df[infos[v].value_column] = df2[infos[v].value_column]
        return df

    def to_csv(self, file_path: Union[str, Path],
               node_column: str = None,
               step_column: str = None,
               weather_columns: dict[WeatherVariable, str] = None) -> pd.DataFrame:
        """Export all variables to a single CSV."""
        df = self.to_dataframe(node_column, step_column, weather_columns)
        df.to_csv(file_path, index=False)
        return df

    # ------------------------------------------------------------------ #
    # Binary file I/O
    # ------------------------------------------------------------------ #

    def _load(self) -> "WeatherSet":
        if not self.dir_path or not Path(self.dir_path).is_dir():
            raise ValueError("A valid directory is required.")
        if not self.file_names:
            raise ValueError("File names dictionary is required.")
        for v, n in self.file_names.items():
            bin_path = self._weather_file_path(n)
            self[v] = WeatherData.from_file(bin_path)
        self.validate()
        return self

    def _save(self) -> None:
        if not self._dir_path:
            raise ValueError("Directory is required.")
        if not self._file_names:
            raise ValueError("File names are required.")
        make_path(self._dir_path)
        for v, wd in self._weather_dict.items():
            bin_path = self._weather_file_path(self._file_names[v])
            wd.to_file(bin_path)

    @classmethod
    def from_files(cls, dir_path: Union[str, Path],
                   prefix: str = "",
                   file_names: dict[WeatherVariable, str] = None) -> "WeatherSet":
        """Load from existing ``.bin`` / ``.bin.json`` file pairs in a directory."""
        WeatherVariable.validate_types(file_names, [str, Path])
        file_names = file_names or cls.select_weather_files(dir_path=dir_path, prefix=prefix)
        ws = WeatherSet(dir_path=dir_path, file_names=file_names)
        ws._load()
        return ws

    def to_files(self, dir_path: Union[str, Path],
                 file_names: dict[WeatherVariable, str] = None) -> None:
        """Write all ``.bin`` / ``.bin.json`` file pairs to a directory."""
        file_names = file_names or self.make_file_paths()
        self._dir_path = Path(dir_path)
        self._file_names = file_names
        self._save()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _init_weather_columns(cls, weather_columns: dict[WeatherVariable, str | None] = None
                              ) -> dict[WeatherVariable, str]:
        WeatherVariable.validate_types(weather_columns, [str, None])
        if weather_columns:
            weather_variables = list(weather_columns)
        else:
            weather_variables = WeatherVariable.list(exclude=WeatherVariable.LAND_TEMPERATURE)
        weather_columns = weather_columns or {}
        return {v: weather_columns.get(v) or v.value for v in weather_variables}

    @classmethod
    def _init_dataframe_info_dict(cls,
                                  node_column: str = None,
                                  step_column: str = None,
                                  weather_columns: dict[WeatherVariable, str] = None
                                  ) -> tuple[dict[WeatherVariable, DataFrameInfo], dict[WeatherVariable, str]]:
        weather_columns = cls._init_weather_columns(weather_columns)
        info_dict = {
            v: DataFrameInfo(node_column=node_column, step_column=step_column, value_column=weather_columns[v])
            for v in weather_columns
        }
        return info_dict, weather_columns

    @classmethod
    def _make_file_templates(cls,
                             prefix: str = "*",
                             suffix: str = "*{}*.bin",
                             weather_variables: list[WeatherVariable] = None,
                             weather_names: dict[WeatherVariable, str] = None) -> dict[WeatherVariable, str]:
        if prefix is None:
            raise ValueError("Prefix cannot be None.")
        if suffix is None:
            raise ValueError("Suffix cannot be None.")
        WeatherVariable.validate_types(weather_names, [str])

        if not suffix.endswith(".bin") and not suffix.endswith("*"):
            suffix += "*.bin"

        template = prefix + suffix
        template = template.replace("**", "*")

        if not weather_variables:
            weather_variables = WeatherVariable.list(exclude=WeatherVariable.LAND_TEMPERATURE)
        weather_names = weather_names or {v: v.value for v in weather_variables}

        return {v: template.format(weather_names[v]) for v in weather_names}

    @classmethod
    def make_file_paths(cls,
                        dir_path: Union[str, Path] = None,
                        prefix: str = "",
                        suffix: str = "{}.bin",
                        weather_variables: list[WeatherVariable] = None,
                        weather_names: dict[WeatherVariable, str] = None) -> dict[WeatherVariable, str]:
        """Generate conventional EMOD weather file paths."""
        names = cls._make_file_templates(
            prefix=prefix, suffix=suffix,
            weather_names=weather_names, weather_variables=weather_variables,
        )
        if dir_path is not None:
            names = {v: str(Path(dir_path) / n) for v, n in names.items()}
        return names

    @classmethod
    def select_weather_files(cls, dir_path: Union[str, Path],
                             prefix: str = "*",
                             suffix: str = "*{}*.bin",
                             weather_variables: list[WeatherVariable] = None,
                             weather_names: dict[WeatherVariable, str] = None) -> dict[WeatherVariable, str]:
        """Find weather files in a directory by name pattern."""
        if dir_path is None:
            raise ValueError("Directory path is required.")
        templates = cls._make_file_templates(
            prefix=prefix, suffix=suffix,
            weather_names=weather_names, weather_variables=weather_variables,
        )
        names = {}
        for v, pattern in templates.items():
            files = list(Path(dir_path).glob(pattern))
            if len(files) > 1:
                raise ValueError(f"Multiple files match pattern {pattern!r}")
            if len(files) == 1:
                names[v] = files[0].name
        return names

    def _weather_file_path(self, file_name: Union[str, Path]) -> Path:
        return Path(self.dir_path) / str(file_name)

    def validate(self) -> None:
        series_len0 = node_count0 = id_ref0 = resolution0 = years0 = None

        for v, wd in self._weather_dict.items():
            wd.validate()
            wd.metadata.validate()
            wm = wd.metadata

            series_len0 = series_len0 or wm.series_len
            node_count0 = node_count0 or wm.node_count
            id_ref0 = id_ref0 or wm.id_reference
            resolution0 = resolution0 or wm.spatial_resolution
            years0 = years0 or wm.data_years

            label = f" ({self.file_names[v]})" if v in self.file_names else ""
            if series_len0 != wm.series_len:
                raise ValueError(f"series_len mismatch for {v}{label}")
            if node_count0 != wm.node_count:
                raise ValueError(f"node_count mismatch for {v}{label}")
            if id_ref0 != wm.id_reference:
                raise ValueError(f"id_reference mismatch for {v}{label}")
            if resolution0 != wm.spatial_resolution:
                raise ValueError(f"spatial_resolution mismatch for {v}{label}")
            if years0 != wm.data_years:
                raise ValueError(f"data_years mismatch for {v}{label}")

        if self._weather_columns:
            for v in WeatherVariable.list():
                in_data = v in self._weather_dict
                in_cols = v in self._weather_columns
                if in_data != in_cols:
                    raise ValueError(
                        f"Weather variable {v} is in "
                        f"{'data' if in_data else 'columns'} but not "
                        f"{'columns' if in_data else 'data'}."
                    )
