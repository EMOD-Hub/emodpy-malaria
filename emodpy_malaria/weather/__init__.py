import pandas as pd
from typing import Tuple

from emodpy_malaria.weather.weather_utils import *
from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherMetadata, WeatherAttributes
from emodpy_malaria.weather.weather_data import WeatherData, DataFrameInfo
from emodpy_malaria.weather.weather_set import WeatherSet
from emodpy_malaria.weather.weather_request import WeatherRequest, WeatherArgs, RequestReport

from idmtools_platform_comps.comps_platform import COMPSPlatform

# module level doc-string
__doc__ = """
**weather** is a module providing features for working with EMOD weather files.  

Main Features
-------------
Here are main features:
    
  - Generate EMOD weather files locally from a csv file.     
  - Generate EMOD weather files using COMPS SSMT weather service.
  - Convert existing EMOD weather files to csv file or dataframes.
  - Programmatic access to EMOD weather files via weather object model.

"""

# Use __all__ to let type checkers know what is part of the public API.
_all_ = ['csv_to_weather',
         'generate_weather'
         'weather_to_csv',
         'WeatherRequest',
         'WeatherArgs',
         'RequestReport',
         'WeatherMetadata',
         'WeatherAttributes',
         'WeatherData',
         'DataFrameInfo',
         'WeatherSet',
         'WeatherVariable']


def generate_weather(platform: Union[str, COMPSPlatform],
                     site_file: Union[str, Path],
                     start_date: int,
                     end_date: int = None,
                     node_column: str = "nodes",
                     lat_column: str = "lat",
                     lon_column: str = "lon",
                     id_reference: str = None,
                     request_name: str = "",
                     local_dir: Union[str, Path] = None,
                     data_source: str = None,
                     force: bool = False) -> WeatherRequest:
    """
    Generate weather files by submitting a request and downloading generated weather files to a specified dir.

    Args:
        platform: Platform name (like "Bayesian") or COMPSPlatform object, where the work item will run.
        site_file: CSV (.csv) or demographics (.json) file containing a set of sites (points) defined with lat/lon.
                   CSV file must contain columns for: EMOD node ids (node), latitude (lat) and longitude (lon).
                   Demographics file must match EMOD demographics file schema.
        start_date: Start date, in formats: year (2018), year and day-of-year (2018001) or date (20180101)
        end_date: (Optional) End date, in formats: year (2018), year and day-of-year (2018365) or date (20181231)
        node_column: (Optional) Name of a column containing EMOD node ids. The default is "nodes".
        lat_column: (Optional) Name of a column containing site (point) latitude. The default is "lat".
        lon_column: (Optional) Name of a column containing site (point) longitude. The default is "lon".
        id_reference: (Optional) Value of weather metadata IdReference attribute. The default is "Default".
        request_name: (Optional) Name to be used for the weather SSMT work item.
        local_dir: (Optional) Local dir where files will be downloaded.
        data_source: (Optional) SSMT data source to be used.
        force: (Optional) Flag ensuring a new weather request is submitted, even if weather files exist in "local_dir".

            **Example**::

                wr: WeatherRequest = generate_weather(platform="Bayesian",
                                                      site_file="path/to/sites.csv",
                                                      start_date=2015,
                                                      end_date=2016,
                                                      node_column="id",
                                                      local_dir="path/to/weather_dir")

    Returns:
        WeatherRequest object.
        Can be used to access asset collection id or a local dir (if not given as ) argument or a download report.
    """
    wa = WeatherArgs(site_file=site_file,
                     start_date=start_date,
                     end_date=end_date,
                     node_column=node_column,
                     lat_column=lat_column,
                     lon_column=lon_column,
                     id_reference=id_reference)

    wr = WeatherRequest(platform=platform, local_dir=local_dir, data_source=data_source)
    wr.generate(weather_args=wa, request_name=request_name, force=force)
    wr.download(force=force)

    return wr


def csv_to_weather(csv_data: Union[str, Path, pd.DataFrame],
                   node_column: str = "nodes",
                   step_column: str = "steps",
                   weather_columns: Dict[WeatherVariable, str] = None,
                   attributes: WeatherAttributes = None,
                   weather_dir: Union[str, Path] = None,
                   weather_file_names: Dict[WeatherVariable, str] = None) -> WeatherSet:
    """
    Convert a dataframe or csv file, containing node, step and weather columns, into a weather set
    and corresponding weather files, if weather dir is specified.

    Args:
        csv_data: Dataframe or a csv file path, containing weather data.
        node_column: (Optional) Column containing node ids. The default is "nodes". The default is "nodes".
        step_column: (Optional) Column containing node index for weather time series values. The default is "steps".
        weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                         Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".
        attributes: (Optional) Weather attribute object containing metadata for WeatherMetadata object.
        weather_dir: (Optional) Directory where weather files are stored. If not specified files are not created.
        weather_file_names: (Optional) Dictionary of weather variables (keys) and weather .bin file names (values).

            **Example**::

                wa = WeatherAttributes(start_year=2001, end_year=2010)
                ws = csv_to_weather(csv_data="path/to/data.csv", attributes=wa, weather_dir="path/to/weather_dir")
    Returns:
        WeatherSet object.
    """

    if isinstance(csv_data, pd.DataFrame):
        ws = WeatherSet.from_dataframe(df=csv_data,
                                       node_column=node_column,
                                       step_column=step_column,
                                       weather_columns=weather_columns,
                                       attributes=attributes)

    elif isinstance(csv_data, str) or isinstance(csv_data, Path):
        ws = WeatherSet.from_csv(file_path=csv_data,
                                 node_column=node_column,
                                 step_column=step_column,
                                 weather_columns=weather_columns,
                                 attributes=attributes)
    else:
        raise TypeError("The data argument must be a file path or a pandas dataframe.")

    if weather_dir:
        ws.to_files(dir_path=weather_dir, file_names=weather_file_names)

    return ws


def weather_to_csv(weather_dir: Union[str, Path],
                   weather_file_prefix: str = "",
                   weather_file_names: Dict[WeatherVariable, str] = None,
                   csv_file: Union[str, Path] = None,
                   node_column: str = "nodes",
                   step_column: str = "steps",
                   weather_columns: Dict[WeatherVariable, str] = None) -> Tuple[pd.DataFrame, WeatherAttributes]:
    """
    Convert weather files into a dataframe and a .csv file, if csv file path is specified.

    Args:
        weather_dir: Local dir containing weather files.
        weather_file_prefix: (Optional) Weather files prefix, e.g. "dtk_15arcmin\_"
        weather_file_names: (Optional) Dictionary of weather variables (keys) and weather .bin file names (values).
        csv_file: (Optional) The path of a csv file to be generated. If not specified csv file is not created.
        node_column: (Optional) Column containing node ids. The default is "nodes".
        step_column: (Optional) Column containing node index for weather time series values. The default is "steps".
        weather_columns: (Optional) Dictionary of weather variables (keys) and weather column names (values).
                         Defaults are WeatherVariables values are used: "airtemp", "humidity", "rainfall", "landtemp".

            **Example**::

                df, attributes = weather_to_csv(weather_dir="path/to/weather_dir")

    Returns:
        Dataframe and weather attributes objects.
    """
    ws = WeatherSet.from_files(dir_path=weather_dir, prefix=weather_file_prefix, file_names=weather_file_names)
    if csv_file:
        df = ws.to_csv(file_path=csv_file,
                       node_column=node_column,
                       step_column=step_column,
                       weather_columns=weather_columns)
    else:
        df = ws.to_dataframe(node_column=node_column,
                             step_column=step_column,
                             weather_columns=weather_columns)
    wa = ws.attributes

    return df, wa
