import numpy as np
import pandas as pd
import shutil
import tempfile
import unittest

from pathlib import Path
from typing import Dict, Union

from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherMetadata, WeatherAttributes
from emodpy_malaria.weather.weather_data import WeatherData
from emodpy_malaria.weather.weather_set import WeatherSet

from test_weather_data import read_df, read_bin
from test_weather_metadata import read_metafile


class WeatherSetTests(unittest.TestCase):

    def setUp(self) -> None:
        current_dir = Path(__file__).parent
        self.dtk_dir = str(current_dir.joinpath("case_default_names"))
        self.dtk_dir_all = str(current_dir.joinpath("case_default_names_all"))
        self.climate_dir = str(current_dir.joinpath("case_custom_names"))
        self.emod_dir = str(current_dir.joinpath("case_prefix"))
        self.data_all_csv: str = str(current_dir.joinpath("case_csv/data_all.csv"))
        self.data_single_node_all_csv: str = str(current_dir.joinpath("case_csv/data_single_node.csv"))
        self.data_all_defaults_csv: str = str(current_dir.joinpath("case_csv/data_all_default_cols.csv"))
        self.test_dir: Path = Path(tempfile.mkdtemp(suffix="emodpy_malaria_unittests"))
        self.resolution = "15arcmin"
        self.data_all_csv_columns = {
            WeatherVariable.AIR_TEMPERATURE: "temp",
            WeatherVariable.RELATIVE_HUMIDITY: "humid",
            WeatherVariable.RAINFALL: "rain",
            WeatherVariable.LAND_TEMPERATURE: "land",
        }
        self.demo_attributes = WeatherAttributes(reference="demo",
                                                 resolution=self.resolution,
                                                 start_year=2010,
                                                 end_year=2021)

    def tearDown(self) -> None:
        shutil.rmtree(str(self.test_dir))

    def test_weather_variable_eq(self):
        self.assertEqual(WeatherVariable.AIR_TEMPERATURE, WeatherVariable.AIR_TEMPERATURE)
        self.assertNotEqual(WeatherVariable.AIR_TEMPERATURE, WeatherVariable.RELATIVE_HUMIDITY)

    def test_weather_variable_list(self):
        ww = WeatherVariable.list()
        self.assertIn(WeatherVariable.AIR_TEMPERATURE, ww)
        self.assertIn(WeatherVariable.RELATIVE_HUMIDITY, ww)
        self.assertIn(WeatherVariable.RAINFALL, ww)
        self.assertIn(WeatherVariable.LAND_TEMPERATURE, ww)

    def test_weather_variable_list_exclude(self):
        ww1 = [WeatherVariable.RAINFALL, WeatherVariable.RELATIVE_HUMIDITY]
        ww2 = WeatherVariable.list(exclude=ww1)
        self.assertIn(WeatherVariable.AIR_TEMPERATURE, ww2)
        self.assertIn(WeatherVariable.LAND_TEMPERATURE, ww2)
        self.assertEqual(len(ww2), 2)

    # Test helpers
    def test_make_file_templates(self):
        # Select file patterns
        prefix = "dtk_"
        patterns = WeatherSet._make_file_templates(prefix=prefix)

        # Construct explicit names
        prefix = "dtk_15arcmin_"
        suffix = "{}_daily.bin"
        names = WeatherSet._make_file_templates(prefix=prefix, suffix=suffix)

        for v in WeatherVariable.list():
            self.assertEqual(patterns[v], f"dtk_*{v.name.lower()}*.bin")
            self.assertEqual(names[v], f"dtk_15arcmin_{v.name.lower()}_daily.bin")

    def test_select_weather_files_dir_only(self):
        wf = WeatherSet.select_weather_files(self.dtk_dir)
        self.validate_weather_set(wf, 3)

        wf = WeatherSet.select_weather_files(dir_path=self.dtk_dir_all)
        self.validate_weather_set(wf, 4)

    def test_select_weather_files_fixed_prefix(self):
        wf = WeatherSet.select_weather_files(dir_path=self.dtk_dir, prefix="dtk_15")
        self.validate_weather_set(wf, 2)

        wf = WeatherSet.select_weather_files(dir_path=self.dtk_dir, prefix="dtk_2")
        self.validate_weather_set(wf, 1)

    def test_select_weather_files_fixed_prefix_asterisk_suffix(self):
        wf = WeatherSet.select_weather_files(dir_path=self.dtk_dir,
                                             prefix="dtk_2",
                                             suffix="*.bin",
                                             weather_names={WeatherVariable.RAINFALL: "rainfall"})
        self.validate_weather_set(wf, 1)

    def test_select_weather_files_fixed_prefix_tag_suffix(self):
        wf = WeatherSet.select_weather_files(dir_path=self.climate_dir,
                                             prefix="climate_",
                                             suffix="{}.bin",
                                             weather_names={
                                                WeatherVariable.AIR_TEMPERATURE: "t2m",
                                                WeatherVariable.RELATIVE_HUMIDITY: "humid",
                                                WeatherVariable.RAINFALL: "tp"})
        self.validate_weather_set(wf, 3)

    def test_select_weather_files_no_prefix_fixed_suffix(self):
        wf = WeatherSet.select_weather_files(dir_path=self.dtk_dir,
                                             suffix="rainfall_daily.bin",
                                             weather_names={WeatherVariable.RAINFALL: "rainfall"})

        self.validate_weather_set(wf, 1)

    def test_select_weather_files_no_prefix_tag_suffix(self):
        wf = WeatherSet.select_weather_files(dir_path=self.climate_dir,
                                             suffix="{}.bin",
                                             weather_names={
                                                WeatherVariable.AIR_TEMPERATURE: "t2m",
                                                WeatherVariable.RELATIVE_HUMIDITY: "humid",
                                                WeatherVariable.RAINFALL: "tp"})
        self.validate_weather_set(wf, 3)

    def test_weather_variables_property(self):
        ws = WeatherSet.from_csv(self.data_all_defaults_csv)
        self.assertSequenceEqual(ws.weather_variables, WeatherVariable.list())
        self.assertSequenceEqual(ws.weather_variables, list(self.data_all_csv_columns))

    def test_weather_set_eq(self):
        ws1a = WeatherSet.from_files(dir_path=self.dtk_dir_all)
        ws1b = WeatherSet.from_files(dir_path=self.dtk_dir_all)
        ws2 = WeatherSet.from_files(dir_path=self.dtk_dir, prefix="dtk_15")

        self.assertEqual(ws1a, ws1b)
        self.assertNotEqual(ws1a, ws2)

    # Test from/to csv

    def test_from_csv(self):
        ws = WeatherSet.from_csv(self.data_all_defaults_csv)
        self.validate_weather_set(ws)

    def test_from_csv_custom_cols(self):
        ws = WeatherSet.from_csv(file_path=self.data_all_csv,
                                 node_column="node",
                                 step_column="step",
                                 weather_columns=self.data_all_csv_columns)

        self.validate_weather_set(ws)

    def test_from_csv_custom_cols_meta(self):
        ws = WeatherSet.from_csv(file_path=self.data_all_csv,
                                 node_column="node",
                                 step_column="step",
                                 weather_columns=self.data_all_csv_columns,
                                 attributes=self.demo_attributes)

        self.validate_weather_set(ws)

    def test_from_csv_single_node(self):

        weather_columns = {
            WeatherVariable.AIR_TEMPERATURE: "air_temp",
            WeatherVariable.RELATIVE_HUMIDITY: "rel_humid",
            WeatherVariable.RAINFALL: "total_precip"
        }
        ws = WeatherSet.from_csv(file_path=self.data_single_node_all_csv,
                                 node_column="ids",
                                 step_column="time",
                                 weather_columns=weather_columns)

        self.validate_weather_set(ws)
        df = pd.read_csv(self.data_single_node_all_csv)
        for v, wd in ws.items():
            self.assertEqual(wd.metadata.series_len, 2)
            expected_series = [np.float32(v) for v in df[weather_columns[v]]]
            actual_series = list(list(wd.to_dict().values())[0])
            self.assertSequenceEqual(actual_series, expected_series)

        # Access individual weather files
        wd = ws[WeatherVariable.RAINFALL]
        # This below generate error "Steps series is not valid.
        df = wd.to_dataframe()

        # Create all three weather files
        ws.to_files(dir_path=self.test_dir)

        # This below generates error " AssertionError: Please specify weather time series length."
        ws2 = WeatherSet.from_files(dir_path=self.test_dir,
                                    file_names={WeatherVariable.RAINFALL: "dtk_15arcmin_rainfall_daily.bin"})
        self.validate_weather_set(ws2)
    # Test from/to DataFrame

    def test_from_dataframe(self):
        df = read_df(self.data_all_defaults_csv)
        ws = WeatherSet.from_dataframe(df)
        self.validate_weather_set(ws)

    def test_to_dataframe(self):
        ws = WeatherSet.from_csv(self.data_all_defaults_csv)
        df_actual = ws.to_dataframe()
        df_expected = read_df(self.data_all_defaults_csv)
        self.assertTrue(df_expected.equals(df_actual))

    # Test from/to files
    def test_from_files(self):
        ws = WeatherSet.from_files(dir_path=self.dtk_dir_all)
        self.validate_weather_set(ws)
        self._validate_weather_files(dir_path=self.dtk_dir_all, ws=ws)

    def test_from_files_with_prefix(self):
        ws = WeatherSet.from_files(dir_path=self.dtk_dir, prefix="dtk_15arcmin")
        self.validate_weather_set(ws)
        self._validate_weather_files(dir_path=self.dtk_dir, ws=ws)

    def test_from_files_with_prefix_diff_suffix(self):
        ws = WeatherSet.from_files(dir_path=self.emod_dir, prefix="emod_")
        self.validate_weather_set(ws)
        self._validate_weather_files(dir_path=self.emod_dir, ws=ws)

    def test_from_files_with_select(self):
        file_names = WeatherSet.select_weather_files(dir_path=self.dtk_dir,
                                                     prefix="dtk_15arcmin",
                                                     weather_variables=[WeatherVariable.AIR_TEMPERATURE])
        ws = WeatherSet.from_files(dir_path=self.dtk_dir, file_names=file_names)
        self._validate_weather_files(dir_path=self.dtk_dir, ws=ws)

    def test_to_files(self):
        ws: WeatherSet = WeatherSet.from_csv(self.data_all_defaults_csv)

        file_names = WeatherSet.make_file_paths(prefix=f"demo_{self.resolution}_",
                                                weather_variables=ws.weather_variables)

        ws.to_files(dir_path=self.test_dir, file_names=file_names)
        for v, f in file_names.items():
            ff = self.test_dir.joinpath(f)
            self.assertTrue(ff.is_file())
            wd_actual: WeatherData = ws[v]
            wd_expected = WeatherData.from_file(ff)
            self.assertTrue(ff.stat().st_size == wd_expected.metadata.total_value_count*4)
            self.assertTrue(np.array_equal(wd_expected.data, wd_actual.data))

    def test_load_fail_diff_resolution(self):
        """Tests validation of attributes which must be the same in all files in a weather set."""
        with self.assertRaises(AssertionError):
            # This fails because this dir contains files of different resolution.
            ws = WeatherSet.from_files(dir_path=self.dtk_dir)

    def test_load_df_save(self):
        ws1 = WeatherSet.from_files(dir_path=self.dtk_dir, prefix="dtk_15arc")
        ws1.to_csv(file_path=self.test_dir.joinpath("data.csv"))
        df = ws1.to_dataframe()
        ws2 = WeatherSet.from_dataframe(df=df, weather_columns=ws1.weather_columns, attributes=ws1.values()[0].metadata)
        ws2.to_files(self.test_dir)
        ws3 = WeatherSet.from_files(dir_path=self.test_dir)

        self.assertEqual(ws1, ws2)
        self.assertEqual(ws1, ws3)

    def test_edit_selected_files_str(self):
        with self.assertRaises(TypeError):
            WeatherSet.from_files(dir_path=self.dtk_dir,
                                  file_names={"humid": "dtk_15arcmin_relative_humidity_daily.bin"})

    def test_edit_selected_files(self):
        wv = WeatherVariable.RELATIVE_HUMIDITY
        ws = WeatherSet.from_files(dir_path=self.dtk_dir,
                                   file_names={wv: "dtk_15arcmin_relative_humidity_daily.bin"})
        wd = ws.values()[0]
        wd.data[:] += 1000.1

        file_path = self.test_dir.joinpath('test1.csv')
        ws.to_csv(file_path=file_path)

        df_expected = wd.to_dataframe()
        df_actual = read_df(file_path)
        df_expected.columns = df_actual.columns
        self.assertTrue(df_expected.equals(df_actual))

    # Helpers

    def validate_weather_set(self, ws: Union[WeatherSet, Dict[WeatherVariable, Union[str, Path]]], min_count: int = 1):
        weather_variables = list(ws.keys()) or WeatherVariable.list()
        self.assertTrue(isinstance(ws, WeatherSet) or isinstance(ws, Dict))
        self.assertGreaterEqual(len(ws), min_count)
        self.assertEqual(len(ws), len(weather_variables))
        for v, wd in ws.items():
            self.assertIn(v, weather_variables)
            if isinstance(wd, str) or isinstance(wd, Path):
                self.assertEqual(Path(wd).parent, Path())
                continue
            self.assertIsInstance(wd, WeatherData)
            self.assertIsInstance(wd.metadata, WeatherMetadata)
            self.assertGreater(wd.data.shape[0], 0)
            self.assertGreater(wd.data.shape[1], 0)

    def _validate_weather_files(self, dir_path: str, ws: WeatherSet):
        dir_path = Path(dir_path)
        self.assertTrue(dir_path.is_dir())

        self.assertTrue(len(ws.weather_variables) > 0)
        # Load expected
        for v in ws.weather_variables:
            name = str(v.name).lower()
            bin_path = list(dir_path.glob(f"*{name}*.bin"))[0]
            self.assertTrue(bin_path.is_file())
            meta_path = bin_path.with_suffix(".bin.json")
            meta_expected, offset = read_metafile(meta_path)
            data_expected: np.ndarray = read_bin(bin_path)

            wd: WeatherData = ws[v]
            wm: WeatherMetadata = wd.metadata

            # Validate
            self.assertEqual(wm.node_offset_str, offset)
            for k in meta_expected.keys():
                self.assertEqual(wm.attributes_dict[k], meta_expected[k])

            self.assertTrue(np.array_equal(data_expected, wd.data.reshape(-1)))


if __name__ == '__main__':
    unittest.main()
