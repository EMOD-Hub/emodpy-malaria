import os
import tempfile
import unittest

from typing import List

from idmtools_platform_comps.comps_platform import AssetCollection
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

from emodpy_malaria.weather import *

_FILE_COUNT = 8


def ls_glob(local_dir: Union[str, Path]):
    return list(Path(local_dir).glob("*.bin*"))


class WeatherRequestTests(unittest.TestCase):

    def setUp(self) -> None:
        self.platform_name: str = "Calculon"
        self.current_dir: Path = Path(__file__).parent
        self.sites_csv: Path = self.current_dir.joinpath("ssmt/sites.csv")
        self.demographics_json: Path = self.current_dir.joinpath("ssmt/demographics.json")
        self.test_dir: Path = Path(tempfile.mkdtemp(suffix="emodpy_malaria_unittests"))
        # we need asset collection that has files with dtk_15arcmin_ prefix
        self.asset_collection_id = "67a0bb90-c796-ef11-aa19-b8830395dfc5"
        self.dtk_file_prefix = "dtk_15arcmin_"

    def tearDown(self) -> None:
        pass

    @property
    def wa(self):
        return WeatherArgs(site_file=str(self.sites_csv), start_date=2015, node_column="nodes")

    @property
    def wr(self) -> WeatherRequest:
        return WeatherRequest(platform=self.platform_name, is_staging=False)

    # WeatherArgs tests

    def test_weather_args_init(self):
        self.wa.validate()

    # WeatherRequest tests
    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_init(self):
        wr = self.wr
        self.assertEqual(wr._platform.environment, self.platform_name)
        self.assertTrue(Path(wr.local_dir).is_dir())
        self.assertEqual(wr._create_asset, True)
        self.assertEqual(wr._image, "idm-docker-production.packages.idmod.org/dse/weather-files")

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_command(self):
        wr = self.wr
        command = wr._construct_command(self.wa)
        self.assertTrue(command.startswith("python /app/generate_weather_asset_collection.py"))
        self.assertIn(wr._data_source.name, command)
        self.assertIn(self.wa.site_file.name, command)
        self.assertIn(ymd(self.wa.start_date), command)
        self.assertIn(ymd(self.wa.end_date), command)
        self.assertIn(self.wa.node_column, command)

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_work_item(self):
        name = "ERA5 work item"
        wr = WeatherRequest(platform=self.platform_name)
        command = wr._construct_command(self.wa)
        wi = wr._init_work_item(weather_args=self.wa, name=name, command=command)
        self.assertIsInstance(wi, SSMTWorkItem)
        self.assertEqual(wi.name, name)
        self.assertEqual(wi.transient_assets.count, 1)
        self.assertEqual(wi.transient_assets[0].filename, self.sites_csv.name)
        self.assertIn("weather", list(wi.tags))
        self.assertIn(wr._data_source.name, list(wi.tags))

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_asset_collection(self):
        wr = self.wr
        asc = wr._fetch_asset_collection(asset_collection_id=self.asset_collection_id)
        self.assertIsInstance(asc, AssetCollection)
        self.assertEqual(len(asc.assets), _FILE_COUNT)
        for f in asc.assets:
            self.assertTrue(f.filename.startswith(self.dtk_file_prefix))

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_asset_files(self):
        wr: WeatherRequest = WeatherRequest(platform=self.platform_name)
        wr.local_dir = self.test_dir    # Not needed
        self._validate_file_list(wr.files)

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_download_only(self):
        WeatherRequest(platform=self.platform_name).download(data_id=self.asset_collection_id, local_dir=self.test_dir)
        files = ls_glob(self.test_dir)
        self._validate_file_list(files)
        self._validate_file_read(files)

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_generate_download(self):
        wr1 = self._run_generate_test().download()
        self._validate_download_report(wr=wr1)

        wr2 = self._run_generate_test(sites_file=self.demographics_json).download()
        self._validate_download_report(wr=wr2)

        ws1 = WeatherSet.from_files(wr1.local_dir)
        ws2 = WeatherSet.from_files(wr2.local_dir)
        self.assertEqual(ws1, ws2)

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_weather_request_download_existing(self):
        wr = self._run_generate_test()
        report = wr.download(local_dir=self.test_dir).report.download
        files = ls_glob(self.test_dir)

        self._validate_file_list(files)
        self.assertEqual(self.test_dir, wr.local_dir)

        # Confirm all files are downloaded
        self.assertEqual(len(files), _FILE_COUNT)
        self.assertEqual(len(files), len(report["ok"]))
        self._validate_download_report(wr)

        # Confirm all files are skipped
        self._validate_download_report(wr=wr.download(), ok_count=0, skip_count=_FILE_COUNT)

        # Remove one file
        [f for f in files if "air" in f.name][0].unlink()
        files3a = ls_glob(self.test_dir)
        self.assertEqual(len(files3a), _FILE_COUNT - 1)

        # Confirm only one file is downloaded.
        self._validate_download_report(wr=wr.download(), ok_count=1, skip_count=_FILE_COUNT-1)

    def _validate_file_list(self, files: Union[List[str], List[Path]]):
        files = [Path(f) for f in files]
        self.assertEqual(len(files), _FILE_COUNT)
        for f in files:
            self.assertTrue(f.name.startswith(self.dtk_file_prefix))

    def _validate_file_read(self, files: List):
        for f in files:
            is_bin = str(f).endswith(".bin")
            ww = WeatherData.from_file(f) if is_bin else WeatherMetadata.from_file(f)
            if is_bin:
                self.assertTrue(len(ww.data.reshape(-1)) > 0)
            else:
                ww.validate()

    def _validate_download_report(self, wr: WeatherRequest, ok_count=_FILE_COUNT, skip_count=0):
        report = wr.report.download
        self.assertEqual(ok_count + skip_count, _FILE_COUNT)
        self.assertEqual(len(report["ok"]), ok_count)
        self.assertEqual(len(report["skip"]), skip_count)

    def _run_generate_test(self, sites_file: Union[str, Path] = None):
        sites_file = sites_file or self.sites_csv
        wa = WeatherArgs(site_file=sites_file,
                         start_date=2015,
                         end_date=20150103,
                         node_column="nodes")

        wr = WeatherRequest(platform=self.platform_name)

        wr.generate(weather_args=wa)

        self.assertEqual(len(str(wr.data_id)), 36)
        self._validate_file_list(wr.files)

        return wr


if __name__ == '__main__':
    unittest.main()
