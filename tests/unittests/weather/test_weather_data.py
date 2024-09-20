import shutil
import numpy as np
import pandas as pd
import tempfile
import unittest

from pathlib import Path
from typing import Dict, List

from emodpy_malaria.weather.weather_metadata import WeatherMetadata, WeatherAttributes
from emodpy_malaria.weather.weather_data import WeatherData, DataFrameInfo
from test_weather_metadata import read_metafile


class WeatherDataTests(unittest.TestCase):

    def setUp(self) -> None:
        # Prepared files
        self.current_dir = Path(__file__).parent
        air_temp_path = 'case_default_names/dtk_15arcmin_air_temperature_daily.bin'
        self.case_dtk_data_file = str(self.current_dir.joinpath(air_temp_path))
        self.case_dtk_meta_file = str(self.current_dir.joinpath(f"{self.case_dtk_data_file}.json"))
        self.csv_path = str(self.current_dir.joinpath("case_csv/data.csv"))
        # New files
        self.test_dir = tempfile.mkdtemp(suffix="emodpy_malaria_unittests")
        self.test_data_file = Path(self.test_dir).joinpath("new_file.bin")
        self.test_meta_file = f"{self.test_data_file}.json"
        # Node series
        self.distinct_node_series = {
            10: np.array([1., 2., 3.]),
            20: [4., 5., 6.],
            30: [7., 8., 9.],
        }

        self.repeated_node_series = {
            10: np.array([1., 2., 3.]),
            20: [4., 5., 6.],
            30: [1., 2., 3.],
        }
        self.same_nodes = {10: [30]}
        self.unique_node_series = {
            10: [1., 2., 3.],
            20: [4., 5., 6.]
        }

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_dataframe_info_init(self):
        info1 = DataFrameInfo()
        self.assertEqual(info1.node_column, "nodes")
        self.assertEqual(info1.step_column, "steps")
        self.assertEqual(info1.value_column, "values")
        info2 = DataFrameInfo(node_column="nodes")
        self.assertEqual(info1, info2)

        info3 = DataFrameInfo(node_column="nodes123")
        self.assertEqual(info3.node_column, "nodes123")
        self.assertEqual(info3.step_column, "steps")
        self.assertEqual(info3.value_column, "values")

    def test_dataframe_info_detect_columns(self):
        data_dict = {"node_ids": [1, 1, 2, 2, 3, 3], "step": [1, 2, 1, 2, 1, 2], "data": [1.1, 1.2, 2.3, 2.4, 3.5, 3.6]}
        df = pd.DataFrame(data_dict)
        actual_info = DataFrameInfo.detect_columns(df)
        expected_info = DataFrameInfo(node_column="node_ids", step_column="step", value_column="data")
        self.assertEqual(expected_info, actual_info)

    def test_data_create_no_metadata(self):
        data = np.array([[1, 2, 3], [4, 5, 6]])
        wd = WeatherData(data=data)
        self.assertTrue(np.array_equal(wd.data, data))
        self.assertSequenceEqual(wd.metadata.nodes, [1, 2])
        self.assertEqual(wd.metadata.node_offset_str, "0000000100000000000000020000000c")

    def test_data_create(self):
        nodes = [1, 2]
        data = np.array([[1, 2, 3], [4, 5, 6]])
        meta = WeatherMetadata(
            node_ids=nodes,
            series_len=3,
            attributes=WeatherAttributes(
                start_year=2001,
                end_year=2010,
                provenance="Weather unittest file."))

        wd = WeatherData(data=data, metadata=meta)
        self.assertTrue(np.array_equal(wd.data, data))
        self.assertSequenceEqual(wd.metadata.nodes, nodes)
        self.assertEqual(wd.metadata.node_offset_str, "0000000100000000000000020000000c")

    def test_data_read(self):
        wd: WeatherData = WeatherData.from_file(self.case_dtk_data_file)
        wm = wd.metadata
        expected_meta, expected_offset = read_metafile(self.case_dtk_meta_file)

        self.assertEqual(expected_meta['Author'], wm.author)
        self.assertEqual(expected_offset, wm.node_offset_str)

        expected_data = read_bin(self.case_dtk_data_file)
        self.assertEqual(wd.data.shape, (wm.series_count, wm.series_len))
        self.assertTrue(np.array_equal(expected_data, wd.data.reshape(-1)))

    def test_to_dict(self):
        wd1 = WeatherData.from_dict(node_series=self.repeated_node_series)
        data_dict1 = wd1.to_dict()

        wd2 = WeatherData.from_dict(node_series=self.unique_node_series, same_nodes=self.same_nodes)
        data_dict2 = wd2.to_dict(only_unique_series=True)
        n1 = list(data_dict1)[0]
        n2 = list(data_dict1)[1]
        n3 = list(data_dict1)[2]

        self.assertSequenceEqual(list(data_dict1[n1]), list(data_dict2[n1]))
        self.assertSequenceEqual(list(data_dict1[n2]), list(data_dict2[n2]))
        self.assertSequenceEqual(list(data_dict1[n3]), list(data_dict2[n1]))
        self.assertTrue(n3 not in data_dict2)
        self.assertTrue(all(data_dict1[n1] != data_dict1[n2]))

    def test_from_dict(self):
        wd1 = WeatherData.from_dict(node_series=self.repeated_node_series)
        wd2 = WeatherData.from_dict(node_series=self.unique_node_series, same_nodes=self.same_nodes)

        self.assertSequenceEqual(wd1.metadata.nodes, wd2.metadata.nodes)

    def test_from_dict_with_metadata(self):
        # Specify node ids and weather time series
        data = {
            10: [20.1, 20.2, 20.3],
            20: [20.4, 20.5, 20.6]
        }

        # Specify basic metadata (recommended, optional).
        attributes = WeatherAttributes(start_year=2001,
                                       end_year=2010,
                                       provenance="Weather unittest file.")

        # Initialize a weather data object.
        wd = WeatherData.from_dict(node_series=data, attributes=attributes)

        expected_array = np.array(list(data.values()), dtype=np.float32)
        self.assertTrue(np.array_equal(expected_array, wd.data))
        self.assertEqual(wd.metadata.data_years, attributes.data_years)
        self.assertEqual(wd.metadata.provenance, attributes.provenance)

    def test_to_dataframe(self):
        wd1 = WeatherData.from_dict(node_series=self.repeated_node_series)
        df1 = wd1.to_dataframe()

        wd2 = WeatherData.from_dict(node_series=self.unique_node_series, same_nodes=self.same_nodes)
        df2 = wd2.to_dataframe(info=DataFrameInfo(only_unique_series=True))

        nodes = list(set(df1.nodes))
        n1 = nodes[0]
        n2 = nodes[1]
        n3 = nodes[2]

        self.assertTrue(isinstance(df1, pd.DataFrame))
        self.assertTrue(isinstance(df2, pd.DataFrame))

        # The difference is that df1 has n3
        self.assertTrue(df1[df1.nodes != n3].equals(df2))

        # Data for n1 and n3 are the same.
        dff1 = df1[df1.nodes == n3][df1.columns.values[1:]].reset_index(drop=True)
        dff2 = df2[df2.nodes == n1][df2.columns.values[1:]].reset_index(drop=True)
        self.assertTrue(dff1.equals(dff2))

        # Data for n1 and n2 is different.
        dff11 = df1[df1.nodes == n1][df1.columns.values[1:]].reset_index(drop=True)
        dff22 = df2[df2.nodes == n2][df2.columns.values[1:]].reset_index(drop=True)
        self.assertFalse(dff11.equals(dff22))

    def test_from_dataframe_distinct(self):
        wd = self._from_dataframe_test(self.distinct_node_series)
        offsets = list(wd.metadata.node_offsets.values())
        self.assertEqual(len(set(offsets)), len(offsets))

    def test_from_dataframe_repeated(self):
        wd = self._from_dataframe_test(self.repeated_node_series)
        offsets = list(wd.metadata.node_offsets.values())
        self.assertEqual(offsets[0], offsets[-1])

    def _from_dataframe_test(self, node_series: Dict[int, List[int]]):
        nodes = list(node_series.keys())
        node_count = len(nodes)
        series_len = len(list(node_series.values())[0])
        total_values = node_count * series_len
        node_list = np.repeat(nodes, series_len)
        step_list = list(range(1, series_len + 1)) * node_count
        data_list = np.array(list(node_series.values())).reshape(total_values)

        df = pd.DataFrame({"nodes": node_list, "step": step_list, "data": data_list})
        wd = WeatherData.from_dataframe(df)

        self.assertSequenceEqual(nodes, wd.metadata.nodes)

        expected_values = data_list[:wd.metadata.total_value_count]
        actual_values = wd.data.reshape(wd.metadata.total_value_count)
        self.assertTrue(np.array_equal(expected_values, actual_values))

        return wd

    def test_to_csv(self):
        expected_csv_path = str(self.current_dir.joinpath("case_csv/data.csv"))
        expected_df = read_df(expected_csv_path)
        wd = WeatherData.from_dataframe(expected_df)

        actual_csv_path = str(Path(self.test_dir).joinpath(Path(expected_csv_path).name))
        wd.to_csv(actual_csv_path)
        actual_df = read_df(actual_csv_path)
        self.assertFalse(sorted(expected_df.columns.values) == sorted(actual_df.columns.values))

        # nodes,step,data
        wd.to_csv(actual_csv_path, info=DataFrameInfo(*expected_df.columns.values))
        actual_df = read_df(actual_csv_path)
        self.assertTrue(expected_df.equals(actual_df))

    def test_from_csv(self):
        df = read_df(self.csv_path)
        values = np.array(df["data"])

        wd = WeatherData.from_csv(self.csv_path)
        actual_values = wd.data.reshape(-1)
        expected_values = values.reshape(-1)[:len(actual_values)]
        self.assertTrue(np.array_equal(expected_values, actual_values))

    def test_edit_file(self):
        wd: WeatherData = WeatherData.from_file(self.case_dtk_data_file)
        wm = wd.metadata

        new_data_value = 1012
        new_meta_value = "test_edit_file"

        wd.data[1, 2] = new_data_value
        wm.provenance = new_meta_value

        wd.to_file(self.test_data_file)

        actual_meta, _ = read_metafile(self.test_meta_file)
        self.assertEqual(actual_meta["DataProvenance"], new_meta_value)

        actual_bin = read_bin(self.test_data_file).reshape(wd.data.shape)
        self.assertEqual(actual_bin[1, 2], new_data_value)
        self.assertTrue(np.array_equal(actual_bin, wd.data))

    def test_add_node(self):
        wd: WeatherData = WeatherData.from_file(self.case_dtk_data_file)
        data_dict = wd.to_dict()

        series = list(data_dict.values())[0].copy()
        series[0] = 888
        data_dict[999] = series

        wd2 = WeatherData.from_dict(node_series=data_dict, attributes=wd.metadata)

        self.assertEqual(wd.data.shape[0] + 1, wd2.data.shape[0])
        self.assertTrue(len(wd.metadata.nodes) + 1, len(wd2.metadata.nodes))

    def test_from_dataframe_exceptions(self):
        with self.assertRaises(TypeError):
            WeatherData.from_dataframe([1, 2, 3])

        with self.assertRaises(ValueError):
            df = pd.DataFrame({"nodes": [], "steps": [], "series": []})
            WeatherData.from_dataframe(df)

    def test_from_dataframe_nan(self):
        df_all = read_df(self.csv_path)
        for c in df_all.columns:
            df = df_all.copy()
            df.loc[1, c] = np.NAN   # picking 2nd row is arbitrary
            with self.assertRaises(ValueError):
                WeatherData.from_dataframe(df)

    def test_from_dict_exceptions(self):
        with self.assertRaises(TypeError):
            WeatherData.from_dict([1, 2])

        with self.assertRaises(ValueError):
            WeatherData.from_dict({})

        with self.assertRaises(ValueError):
            WeatherData.from_dict({10: 123})

        with self.assertRaises(ValueError):
            WeatherData.from_dict({10: []})

        with self.assertRaises(ValueError):
            WeatherData.from_dict({10: [1, 2], 20: [3]})

        with self.assertRaises(ValueError):
            WeatherData.from_dict({10: ['a']})

        with self.assertRaises(ValueError):
            WeatherData.from_dict({10: [np.nan]})

    def test_from_dict_inf(self):
        one: np.float64 = 1.0000000000000000000000000000000000000e787874384034930490301
        with self.assertRaises(ValueError):
            d = self.distinct_node_series.copy()
            d[10][0] = np.float64(np.finfo(np.float32).min) - one
            WeatherData.from_dict(node_series=d)

        with self.assertRaises(ValueError):
            d = self.distinct_node_series.copy()
            d[10][0] = np.float64(np.finfo(np.float32).max) + one
            WeatherData.from_dict(node_series=d)

    def test_from_dict_single_value(self):
        d = {10: [1.1]}
        wd = WeatherData.from_dict(node_series=d)
        self.assertTrue(np.array_equal(wd.data, np.array([[1.1]], dtype=np.float32)))

    # Helpers


def read_bin(file_path) -> np.ndarray:
    data: np.ndarray = np.fromfile(str(file_path), dtype=np.float32)
    return data


def read_df(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    for c in df.columns.values:
        if c in ["nodes", "node", "ids", "step", "steps", "time"]:
            df[c] = df[c].astype(int)
        else:
            df[c] = df[c].astype(np.float32)

    return df


if __name__ == '__main__':
    unittest.main()
