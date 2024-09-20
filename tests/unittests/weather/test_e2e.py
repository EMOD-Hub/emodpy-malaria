import os
import shutil
import subprocess
import unittest
import numpy as np
import pandas as pd

from pathlib import Path

from emodpy_malaria.weather import *


class WeatherE2ETests(unittest.TestCase):
    testfiles_dir = Path(__file__).parent.joinpath("scenarios")

    def setUp(self) -> None:
        # create output folder
        shutil.rmtree(self.testfiles_dir.joinpath("output_data"), ignore_errors=True)
        os.makedirs(self.testfiles_dir.joinpath("output_data"))
        self.series = []
        self.nodeids = [i +100 for i in list(range(1,11,1))]
        # generate 10 data points for 10 nodes
        for i in range(1, 11, 1):
            self.series.append(np.sin(np.linspace(0, 2 * np.pi, 10)) + i)

    def test_generate_weather_from_numpy(self):
        filename = self.testfiles_dir.joinpath("output_data/test_numpy.bin")
        data = np.array(self.series)
        # generate metadata
        wm = WeatherMetadata(node_ids=self.nodeids,
                             series_len=10,
                             attributes={'IdReference':'Xsin', 'custom':'numpy'})
        wd = WeatherData(data=data, metadata=wm)
        wd.to_file(filename)

        # try load it
        wd2 = WeatherData.from_file(filename)
        assert np.all(np.round(wd.data - data, 5)==0), 'data should be the same'
        assert wd.metadata.id_reference == 'Xsin', 'IdReference should be set'
        assert wd.metadata.attributes_dict['custom'] == 'numpy', 'Custom attributes should be set'

    def test_generate_weather_from_dict(self):
        filename = self.testfiles_dir.joinpath("output_data/test_dict.bin")
        data = dict(zip(self.nodeids, self.series))
        attr = WeatherAttributes({'custom':'dict'})
        wd = WeatherData.from_dict(node_series=data, attributes=attr)
        wd.to_file(filename)
        # try load it
        wd2 = WeatherData.from_file(filename)
        assert np.all(np.round(wd.data - wd2.data, 5) == 0), 'data should be the same'
        assert wd.metadata.attributes_dict['custom'] == 'dict', 'Custom attributes should be set'
        data2 = wd2.to_dict()
        shared = {key: data[key] for key in data if key in data2 and np.all(np.round(data[key]) == np.round(data2[key]))}
        assert len(shared) == len(data.keys()), 'dict should be the same'

    def test_generate_weather_from_dict_same_node(self):
        filename = self.testfiles_dir.joinpath("output_data/test_dict2.csv")
        data = dict(zip(self.nodeids, self.series))
        attr = WeatherAttributes({'IdReference': 'Xsin', 'custom': 'dict2'})
        same_nodes = {101: [1101, 1102, 1103]}
        wd = WeatherData.from_dict(node_series=data, same_nodes=same_nodes, attributes=attr)
        df = wd.to_dataframe()
        for n in same_nodes[101]:
            assert list(df[df.nodes==101]['values']) == list(df[df.nodes==n]['values']), 'same nodes should duplicate values as node 101'
        info = DataFrameInfo(node_column="my_id",
                             step_column="timestep",
                             value_column="sin(x)")
        wd.to_csv(filename, info=info)
        wd2 = WeatherData.from_csv(filename, info=info)
        assert np.all(np.round(wd.data - wd2.data, 5) == 0), 'data should be the same'

    def test_nodeid_out_of_range(self):
        filename = self.testfiles_dir.joinpath("input_data/badtestdata.csv")
        weather_columns = {
            WeatherVariable.AIR_TEMPERATURE: "Basel Temperature [2 m elevation corrected]",
            WeatherVariable.RELATIVE_HUMIDITY: "Basel Relative Humidity [2 m]"
        }
        with self.assertRaises(expected_exception=ValueError) as exc:
            ws = WeatherSet.from_csv(file_path=filename,
                                 node_column="location",
                                 step_column="timestep",
                                 weather_columns=weather_columns)
        expected_message = 'Node values must be integers in (0, 4294967295] interval'
        assert(expected_message in str(exc.exception))

    def test_generate_weather_from_csv(self):
        # test both single and multiple nodes
        testfiles = [self.testfiles_dir.joinpath("input_data",f) for f in os.listdir(self.testfiles_dir.joinpath("input_data")) if 'mytestdata' in f]
        for filename in testfiles:
            output_filename = str(filename).replace('input_data', 'output_data')
            weather_columns = {
                WeatherVariable.AIR_TEMPERATURE: "Basel Temperature [2 m elevation corrected]",
                WeatherVariable.RELATIVE_HUMIDITY: "Basel Relative Humidity [2 m]"
            }

            meta = WeatherAttributes(
                start_year=2022,
                end_year=2022)
            ws = WeatherSet.from_csv(file_path=filename,
                                     node_column="location",
                                     step_column="timestep",
                                     weather_columns=weather_columns, attributes=meta)
            # Modify individual weather files
            wd = ws[WeatherVariable.AIR_TEMPERATURE]
            wd.data[0][0] +=1
            wd.to_csv(file_path=output_filename)
            wd2 =  WeatherData.from_csv(output_filename)
            assert (np.all(abs(wd.data-wd2.data)<1e-5))

    def test_existing_bin_files(self):
        ws = WeatherSet.from_files(dir_path=self.testfiles_dir.joinpath("input_data"), prefix="mewu_")
        rainfall = ws.to_dataframe(node_column='ids', step_column='time', weather_columns={WeatherVariable.RAINFALL: "total_precip"})
        assert 'total_precip' in rainfall.columns

        # Access individual weather files
        wd = ws[WeatherVariable.RAINFALL]
        wdf = wd.to_dataframe()
        result = pd.merge(rainfall, wdf, left_on=['ids', 'time'], right_on=['nodes', 'steps'])
        assert np.all(abs(result['total_precip'] - result['values']) < 1e-5)

        # Create all three weather files
        ws.to_files(dir_path=self.testfiles_dir.joinpath('output_data/my_weather'))
        ws2 = WeatherSet.from_files(dir_path=self.testfiles_dir.joinpath('output_data/my_weather'), file_names={WeatherVariable.RAINFALL:"dtk_15arcmin_rainfall_daily.bin"})
        wd2 = ws2[WeatherVariable.RAINFALL]
        assert np.all(wd2.data == wd.data), 'Data should be the same after saved'
        attributes_dict = wd.metadata.attributes_dict
        assert len([k for k in attributes_dict if attributes_dict[k] == attributes_dict[k]]) == len(attributes_dict)
        ws2.to_csv(file_path=self.testfiles_dir.joinpath('output_data/my_weather/test1.csv'))

    def test_null(self):
        weather_columns = {
            WeatherVariable.AIR_TEMPERATURE: "air_temp",
            WeatherVariable.RELATIVE_HUMIDITY: "rel_humid",
            WeatherVariable.RAINFALL: "total_precip"
        }

        with self.assertRaises(ValueError):
            ws = WeatherSet.from_csv(file_path=self.testfiles_dir.joinpath('input_data/data_null.csv'),
                                     node_column="ids",
                                     step_column="time",
                                     weather_columns=weather_columns)
