#!/usr/bin/env python3

"""
Weather service methods for submitting and working with weather data requests.
"""

from __future__ import annotations

import json
import pandas as pd
import tempfile

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Tuple, Union

from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.relation_type import RelationType
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.comps_platform import AssetCollection
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

from emodpy_malaria.weather.data_sources import _get_data_source_metadata
from emodpy_malaria.weather.weather_utils import make_path, parse_date, ymd
from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import _META_DEFAULT_ID_REFERENCE
from emodpy_malaria.weather.weather_set import WeatherSet

_DATE_MIN = datetime(year=2000, month=1, day=1)
_DATE_MAX = datetime(year=2030, month=12, day=31)


class WeatherArgs:
    """Arguments defining weather request space and time scope."""
    def __init__(self,
                 site_file: Union[str, Path],
                 start_date: Union[int, str, datetime],
                 end_date: Union[int, str, datetime] = None,
                 node_column: str = "node",
                 lat_column: str = "lat",
                 lon_column: str = "lon",
                 id_reference: str = _META_DEFAULT_ID_REFERENCE):
        """
        Initializes and validates weather arguments.

        Args:
            site_file: CSV (.csv) or demographics (.json) file containing a set of sites (points) defined with lat/lon.
                       CSV file must contain columns for: EMOD node ids (node), latitude (lat) and longitude (lon).
                       Demographics file must match EMOD demographics file schema.
            start_date: Start date, in formats: year (2018), year and day-of-year (2018001) or date (20180101)
            end_date: (Optional) End date, in formats: year (2018), year and day-of-year (2018365) or date (20181231)
            node_column: (Optional) Name of a column containing EMOD node ids. The default is "nodes".
            lat_column: (Optional) Name of a column containing site (point) latitude.
            lon_column: (Optional) Name of a column containing site (point) longitude.
            id_reference: (Optional) Value of weather metadata IdReference attribute. Default is "Default".
        """

        self.site_file: Path = Path(site_file)

        end_date = end_date or start_date
        start_date = start_date if isinstance(start_date, datetime) else parse_date(start_date, 1, 1)
        end_date = end_date if isinstance(end_date, datetime) else parse_date(end_date, 12, 31)
        self.start_date: datetime = start_date
        self.end_date: datetime = end_date

        self.node_column: str = node_column or "nodes"
        self.lat_column: str = lat_column or "lat"
        self.lon_column: str = lon_column or "lon"
        self.id_reference = id_reference or _META_DEFAULT_ID_REFERENCE
        self.validate()

    def validate(self):
        """Validates: site file (exists, is readable, and it contains specified columns) and dates range."""
        f = self.site_file

        # Validate sites file
        assert f.is_file(), f"File not found: {str(f)}"
        if f.suffix == ".json":
            # Sites demographics file, sanity checks.
            content = json.loads(f.read_text())
            assert len(content["Nodes"]) > 0, f"Invalid demographics file: {str(f)}, "
            for node in content["Nodes"]:
                assert -90 < node["NodeAttributes"]["Latitude"] < 90
                assert -180 < node["NodeAttributes"]["Longitude"] < 180 or 0 < node["NodeAttributes"]["Longitude"] < 360
        else:
            # Sites .csv file
            df = pd.read_csv(f)
            assert len(df) > 0, f"Invalid sites file: {str(f)}"

            # Validate column names
            msg = "Correct {name} column must be specified."
            cols = df.columns.values
            assert self.node_column and self.node_column in cols, msg.format("node")
            assert self.lat_column and self.lat_column in cols, msg.format("latitude")
            assert self.lon_column and self.lon_column in cols, msg.format("longitude")

        # Validate year range
        assert _DATE_MIN <= self.start_date <= self.end_date <= _DATE_MAX, "Start and end years are not valid."


class RequestReport:
    """Specifies an object containing weather request operational reports."""
    download: Dict[str, List[str]] = None   # Status of downloaded files: ok, fail, skip.


class DataSource:
    def __init__(self, name: str = None):
        """Initiate DataSource object based on name. If name is not provided the default is used."""
        # TODO: Implement methods to retrieve the list of available data sources (when supported by the service)
        self._content = _get_data_source_metadata()
        assert "defaults" in self._content and "name" in self._content["defaults"]
        assert "data_sources" in self._content
        if name and name not in self._content["data_sources"]:
            raise ValueError(f"Unsupported datasource name {name}.")

        self._name = name or self._content["defaults"]["name"]

    @property
    def name(self) -> str:
        """Data source name property."""
        return self._name

    @property
    def file_prefix(self) -> str:
        """Weather file prefix based on the current data source resolution."""
        # TODO: Consider a case when a data source supports more than one resolution.
        arc_min = int(self._info["arc_seconds"][0]/60)
        return f"dtk_{arc_min}arcmin_"

    @property
    def weather_variables(self) -> List[WeatherVariable]:
        """List of weather variables supported by the current data source."""
        return [v for v in WeatherVariable.list() if v.name in self._info["weather_variables"]]

    @property
    def _info(self) -> Dict[str]:
        """Info dictionary for the current data source."""
        return self._content["data_sources"][self._name]


class WeatherRequest:
    """Functionality for requesting and downloading weather files. Leverages idmtools API for COMPS SSMT."""
    _image: str = "idm-docker-{}.packages.idmod.org/dse/weather-files"  # weather tool image name.
    _create_asset: bool = True         # flag to indicate creation of a weather asset.
    _platform: COMPSPlatform = None    # The name of COMPS platfrom on which to run the SSMT work item.

    def __init__(self, platform: Union[str, COMPSPlatform], local_dir: str = None, data_source: str = None, is_staging: bool = None):
        """
        Initializes a weather request per specified time-space, weather files and SSMT arguments.

        Args:
            platform: SSMT platform name or COMPSPlatform object. Determined where the work item will run.
            local_dir: (Optional) Local dir where files will be downloaded. If not specified a temp dir is created.
            data_source: (Optional) Data source name to be used by SSMT platform.
            is_staging: (Optional) Flag determining weather image. By default, set based on the platform endpoint.
        """

        # Initialize the platform object
        platform = platform or Platform("SLURMStage")
        self._platform = platform if isinstance(platform, COMPSPlatform) else Platform(platform)
        is_staging = is_staging or self._platform.endpoint == "https://comps2.idmod.org"
        self._image = self._image.format("staging" if is_staging else "production")
        # Exposed as properties
        self._local_dir: Union[str, None] = local_dir
        self._data_source: DataSource = DataSource(data_source)  # The data source name, as used by weather SSMT.
        self._asset_collection_id: Union[str, None] = None
        self._report: RequestReport = RequestReport()

        # Operational
        self._asset_file_tuples: Union[List[Tuple[str, Path]], None] = None

    @property
    def data_id(self) -> str:
        """Expose asset collection id as interface data id property."""
        return self._asset_collection_id

    @data_id.setter
    def data_id(self, value) -> NoReturn:
        """Setter for the data_id property."""
        self._asset_collection_id = value

    @property
    def local_dir(self) -> str:
        """Local dir to/from where weather files will be downloaded."""
        if not self._local_dir:
            self._local_dir = tempfile.mkdtemp()

        return self._local_dir

    @local_dir.setter
    def local_dir(self, value: str) -> NoReturn:
        """Setter for the local_dir property."""
        self._local_dir = str(value)

    @property
    def files(self) -> List[str]:
        """List expected weather file paths."""
        bin_files = WeatherSet.make_file_paths(dir_path=self.local_dir,
                                               prefix=self._data_source.file_prefix,
                                               weather_variables=self._data_source.weather_variables)
        bin_files = list(bin_files.values())
        files = bin_files + [f"{f}.json" for f in bin_files]
        return files

    @property
    def files_exist(self) -> bool:
        """Returns True if all expected weather files exist in the local dir."""
        return all([Path(f).exists() for f in self.files])

    @property
    def report(self) -> RequestReport:
        """Returns report object."""
        return self._report

    @property
    def _asset_files(self) -> List[Tuple[Any, Path]]:
        """Returns a list of tuples of weather asset objects and corresponding file weather names."""
        if self._asset_file_tuples is None:
            assert self._asset_collection_id is not None, "Data id is not set. Either set it or run 'generate'."
            asc = self._fetch_asset_collection(self._asset_collection_id)

            # Transform the list of asset object to (asset, file name) tuples.
            self._asset_file_tuples = [(a, Path(self.local_dir).joinpath(a.filename)) for a in asc]

            # Validate asset file names match expected pattern.
            expected_files = sorted(self.files)
            actual_files = sorted([str(f) for _, f in self._asset_file_tuples])
            odd_files = set(actual_files) - set(expected_files)
            if len(odd_files) > 0:
                print("Warning: Some weather files have unexpected names:")
                print("\n".join(odd_files))

        return self._asset_file_tuples

    def _fetch_asset_collection(self, asset_collection_id) -> AssetCollection:
        """Get asset collection object."""
        asset_collection = self._platform.get_item(item_id=asset_collection_id, item_type=ItemType.ASSETCOLLECTION)
        return asset_collection

    def _construct_command(self, weather_args: WeatherArgs) -> str:
        """
        Constructs SSMT command to run within the weather tool image, to generate weather files.

        Args:
            weather_args: Arguments defining space and time scope and weather files' id reference.

        Returns:
            String representing a command to be run within the weather tool image.
        """
        assert weather_args, "Space and time scope is not defined."
        st = weather_args
        optional_args = f"--ds {self._data_source.name} --id-ref '{st.id_reference}' --node-col '{st.node_column}' "
        optional_args += "--create-asset" if self._create_asset else ""
        command_args = f"{st.site_file.name} {ymd(st.start_date)} {ymd(st.end_date)} {optional_args}"
        command = f"python /app/generate_weather_asset_collection.py {command_args}"
        return command

    def _init_work_item(self, weather_args: WeatherArgs, command: str, name: str = None) -> SSMTWorkItem:
        """
        Initializes SSMT work item.

        Args:
            weather_args: Arguments defining space and time scope and weather files' id reference.
            command: Command to be run within the weather tool image.
            name: Work item name.

        Returns:
            Initialized, ready to run, SSMTWorkItem object.
        """
        st = weather_args

        if not name:
            label = f"{st.site_file.name} {ymd(st.start_date)}-{ymd(st.end_date)}"
            name = f"{self._data_source.name} weather for {label}"

        # Instantiate work item and upload site_details.csv
        wi = SSMTWorkItem(item_name=name, docker_image=self._image, command=command)
        wi.tags = {'weather': None, self._data_source.name: None}
        wi.transient_assets.add_asset(st.site_file)
        return wi

    def generate(self,
                 weather_args: WeatherArgs,
                 request_name: str = None,
                 force: bool = False) -> Union[WeatherRequest, None]:
        """
        Submits the weather request and when data is ready sets the data_id property.

        Args:
            weather_args: Arguments defining space and time scope and weather files' id reference.
            request_name: (Optional) Name to be used for the weather SSMT work item.
            force: (Optional) Force the download, even if target weather files already exist in the local dir.

        Returns:
            Returns this WeatherRequest object (to support method chaining).
        """
        # Skip if files already exist, unless the 'force' flag is set.
        if not force and self.files_exist:
            print("Skipping weather request, files already exist.")
            return self

        self._asset_collection_id: Union[str, None] = None

        # TODO: add date range validation (when supported by the service)

        command = self._construct_command(weather_args=weather_args)
        work_item: SSMTWorkItem = self._init_work_item(weather_args=weather_args,
                                                       command=command,
                                                       name=request_name)
        try:
            # Run work item
            # Note: For simplicity reasons only synchronous scenario is supported (covers the majority of use cases).
            work_item.run(wait_until_done=True)
            comps_wi = work_item.get_platform_object(force=True)

            # Get asset collection and set data id
            acs = comps_wi.get_related_asset_collections(RelationType.Created)
            assert acs and len(acs) > 0, f"Failed to get asset collection for work item {work_item.id}"
            self._asset_collection_id = str(acs[0].id)
            print(f"Generated asset collection ID: {self._asset_collection_id}")
        except ValueError:
            return None

        return self

    def download(self, data_id: str = None, local_dir: Union[str, Path] = None, force: bool = False) -> WeatherRequest:
        """
        Downloads weather files.

        Args:
            data_id: (Optional) Asset collection ID to be downloaded, even if not generated by this request.
            local_dir: (Optional) Local dir where files will be downloaded. If not specified a temp dir is created.
            force: (Optional) Force the download, even if target weather files already exist in the local dir.

        Returns:
            Returns this WeatherRequest object (to support method chaining).
        """
        # Override asset collection id and local dir is specified.
        if data_id:
            self._asset_collection_id = data_id

        if local_dir:
            self._local_dir = local_dir

        # Skip if files already exist, unless the 'force' flag is set.
        if self.files_exist and not force:
            self.report.download = {"ok": [], "fail": [], "skip": self.files}
            print("Skipping download, files already exist.")
            return self

        assert len(self._asset_collection_id) == 36, "Invalid 'asset collection id' length."
        make_path(self._local_dir)

        result = {"ok": [], "fail": [], "skip": []}
        for asset, file_path in self._asset_files:
            assert asset.filename == file_path.name, "Asset and file name do not match."
            try:
                mtime_before = file_path.stat().st_mtime if file_path.is_file() else 0
                if not file_path.is_file() or force:
                    asset.download_to_path(str(file_path), force=force)

                if not file_path.is_file():
                    key = "fail"
                elif file_path.stat().st_mtime > mtime_before:
                    key = "ok"
                else:
                    key = "skip"

            # TODO: More specific exception handling
            except Exception as ex:
                print(str(ex))
                key = "fail"

            result[key].append(str(file_path))

        self.report.download = result
        return self
