"""Weather file creation, reading, and conversion for EMOD simulations.

Main features:

- Create EMOD weather files from CSV, DataFrame, or dictionary data.
- Read existing EMOD weather files into Python objects.
- Convert between EMOD binary weather format and tabular formats.
- Configure EMOD climate model settings.
"""

import pandas as pd

from pathlib import Path
from typing import Union

from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherAttributes, WeatherMetadata
from emodpy_malaria.weather.weather_data import WeatherData, DataFrameInfo
from emodpy_malaria.weather.weather_set import WeatherSet
from emodpy_malaria.weather.weather_config import set_climate_constant, set_climate_by_data

__all__ = [
    "csv_to_weather",
    "weather_to_csv",
    "WeatherVariable",
    "WeatherAttributes",
    "WeatherMetadata",
    "WeatherData",
    "DataFrameInfo",
    "WeatherSet",
    "set_climate_constant",
    "set_climate_by_data",
]


def csv_to_weather(csv_data: Union[str, Path, pd.DataFrame],
                   node_column: str = "nodes",
                   step_column: str = "steps",
                   weather_columns: dict[WeatherVariable, str] = None,
                   attributes: WeatherAttributes = None,
                   weather_dir: Union[str, Path] = None,
                   weather_file_names: dict[WeatherVariable, str] = None) -> WeatherSet:
    """Convert a CSV file or DataFrame to EMOD weather files.

    Args:
        csv_data (Union[str, Path, pd.DataFrame]): Path to CSV file or a pandas DataFrame containing weather
            data with node, step, and weather variable columns.
        node_column (str): Column name for node IDs.
        step_column (str): Column name for time step indices.
        weather_columns (dict[WeatherVariable, str]): ``{WeatherVariable: column_name}`` mapping. If
            omitted, default column names from [WeatherVariable](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/weather/weather_variable/)
            values are used (``airtemp``, ``humidity``, ``rainfall``).
        attributes (WeatherAttributes): Optional metadata attributes for the output files.
        weather_dir (Union[str, Path]): If specified, write ``.bin``/``.bin.json`` files here.
        weather_file_names (dict[WeatherVariable, str]): Optional ``{WeatherVariable: filename}``
            mapping. If omitted, conventional names are generated.

    Returns:
        [WeatherSet](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/weather/weather_set/) containing the parsed weather data.
    """
    if isinstance(csv_data, pd.DataFrame):
        ws = WeatherSet.from_dataframe(
            df=csv_data, node_column=node_column, step_column=step_column,
            weather_columns=weather_columns, attributes=attributes,
        )
    elif isinstance(csv_data, (str, Path)):
        ws = WeatherSet.from_csv(
            file_path=csv_data, node_column=node_column, step_column=step_column,
            weather_columns=weather_columns, attributes=attributes,
        )
    else:
        raise TypeError("csv_data must be a file path or a pandas DataFrame.")

    if weather_dir:
        ws.to_files(dir_path=weather_dir, file_names=weather_file_names)

    return ws


def weather_to_csv(weather_dir: Union[str, Path],
                   weather_file_prefix: str = "",
                   weather_file_names: dict[WeatherVariable, str] = None,
                   csv_file: Union[str, Path] = None,
                   node_column: str = "nodes",
                   step_column: str = "steps",
                   weather_columns: dict[WeatherVariable, str] = None
                   ) -> tuple[pd.DataFrame, WeatherAttributes]:
    """Convert EMOD weather files to a CSV file or DataFrame.

    Args:
        weather_dir (Union[str, Path]): Directory containing ``.bin``/``.bin.json`` file pairs.
        weather_file_prefix (str): File name prefix for auto-detection (e.g.
            ``"namawala_weather"``).
        weather_file_names (dict[WeatherVariable, str]): Explicit ``{WeatherVariable: filename}`` mapping.
        csv_file (Union[str, Path]): If specified, write the output DataFrame to this path.
        node_column (str): Column name for node IDs in the output.
        step_column (str): Column name for time step indices in the output.
        weather_columns (dict[WeatherVariable, str]): ``{WeatherVariable: column_name}`` mapping for
            the output.

    Returns:
        Tuple of (DataFrame, WeatherAttributes).
    """
    ws = WeatherSet.from_files(dir_path=weather_dir, prefix=weather_file_prefix, file_names=weather_file_names)
    if csv_file:
        df = ws.to_csv(
            file_path=csv_file, node_column=node_column,
            step_column=step_column, weather_columns=weather_columns,
        )
    else:
        df = ws.to_dataframe(
            node_column=node_column, step_column=step_column,
            weather_columns=weather_columns,
        )
    return df, ws.attributes
