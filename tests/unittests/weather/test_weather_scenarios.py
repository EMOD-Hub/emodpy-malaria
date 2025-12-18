import os
import tempfile
import unittest

from emodpy_malaria.weather import *
from test_weather_data import read_df
from test_weather_set import WeatherSetTests

@unittest.skip("disabled to avoid comps")
class WeatherScenariosTests(unittest.TestCase):

    def setUp(self) -> None:
        self.platform_name = "Bayesian"
        self.current_dir = Path(__file__).parent
        self.dtk_dir = str(self.current_dir.joinpath("case_default_names"))
        self.dtk_dir_all = str(self.current_dir.joinpath("case_default_names_all"))
        self.dtk_dir_all_csv = str(self.current_dir.joinpath("case_default_names_all", "weather.csv"))
        self.climate_dir = str(self.current_dir.joinpath("case_custom_names"))
        self.data_single_node_all_csv: str = str(self.current_dir.joinpath("case_csv/data_single_node.csv"))
        self.sites_csv = self.current_dir.joinpath("scenarios/site_details.csv")
        self.sites_africa_csv = self.current_dir.joinpath("scenarios/site_details_africa.csv")
        self.input_params_json = self.current_dir.joinpath("scenarios/input_parameters.json")
        self.test_dir = Path(tempfile.mkdtemp(suffix="emodpy_malaria_scenarios"))
        self.test_csv_file = self.test_dir.joinpath("weather.csv")

    def tearDown(self) -> None:
        pass

    def test_csv_to_weather_file(self):
        ws = WeatherSet.from_files(dir_path=self.dtk_dir_all)
        ws_actual = csv_to_weather(csv_data=self.dtk_dir_all_csv,
                                   attributes=ws.attributes,
                                   weather_dir=self.test_dir)
        ws_expected = WeatherSet.from_files(self.test_dir)
        WeatherSetTests().validate_weather_set(ws_actual, 4)
        self.assertEqual(ws_expected, ws_actual)

    def test_csv_to_weather_object(self):
        ws = csv_to_weather(csv_data=self.dtk_dir_all_csv)
        WeatherSetTests().validate_weather_set(ws, 4)

    def test_csv_to_weather_single_node(self):
        weather_columns = {
            WeatherVariable.AIR_TEMPERATURE: "air_temp",
            WeatherVariable.RELATIVE_HUMIDITY: "rel_humid",
            WeatherVariable.RAINFALL: "total_precip"
        }

        ws = csv_to_weather(csv_data=self.data_single_node_all_csv,
                            node_column="ids",
                            step_column="time",
                            weather_columns=weather_columns)

        WeatherSetTests().validate_weather_set(ws, 3)

    def test_weather_to_csv(self):
        df_actual, wa = weather_to_csv(weather_dir=self.dtk_dir_all, csv_file=self.test_csv_file)
        df_expected = read_df(self.dtk_dir_all_csv)
        self.assertTrue(df_expected.equals(df_actual))

    def test_getting_started_readme_example(self):
        weather_dir, weather_dir2 = self.dtk_dir_all, self.test_dir

        # Convert weather files to a dataframe and weather attributes
        df, wa = weather_to_csv(weather_dir=weather_dir)

        # Modify weather data (for example)
        df["airtemp"] += 1.1

        # Generate modified weather files (see "Weather Objects" section
        ws = csv_to_weather(csv_data=df, attributes=wa, weather_dir=weather_dir2)

        # Use WeatherSet object to get programmatic access weather data
        for v in ws.weather_variables:
            print(ws[v].metadata.attributes)    # attributes is a metadata dictionary
            print(ws[v].data.shape)             # data is numpy array

        df_expected = read_df(self.dtk_dir_all_csv)
        df_expected["airtemp"] += 1.1
        ws_expected = WeatherSet.from_files(dir_path=self.dtk_dir_all)

        self.assertTrue(df_expected.equals(df))
        self.assertEqual(ws_expected.attributes, ws.attributes)

    @unittest.skipUnless(os.getenv("WEATHER_LONG_TESTS", False), "Long running")
    def test_generate_climate(self):
        # Amelia script
        # https://github.com/shchen-idmod/archetypes-intervention-impact-idmtools/blob/4bdd6b94f4b534d52fb8a3da3051be3c58210b9b/intervention_impact/run_simulations/02_generate_climate.py#L35

        with open(self.input_params_json) as f:
            instructions = json.loads(f.read())

        for run_type, years in instructions["era5_climate_params"].items():
            start_year, end_year = years["start_year"], years["end_year"]
            print(f"Generating climate for {run_type},  {start_year} to {end_year}")
            this_out_dir = self.test_dir.joinpath("climate", run_type)
            make_path(this_out_dir)

            wr: WeatherRequest = generate_weather(platform=self.platform_name,
                                                  site_file=self.sites_csv,
                                                  start_date=start_year,
                                                  end_date=end_year,
                                                  node_column="id",
                                                  id_reference="Custom user",
                                                  request_name=f"ERA5 weather: {run_type}",
                                                  local_dir=this_out_dir)

            print("Climate file generation submitted. Go to COMPS to monitor and retrieve them.")
            print(f"{run_type} asset id : {wr.data_id}")
            # print(f"{run_type} work item id: {str(wr.entities.work_item.id)}")

            ws = WeatherSet.from_files(wr.local_dir)
            means = {}
            for v in WeatherVariable.list():
                wd: WeatherData = ws[v]
                node_series: Dict[int, np.ndarray[np.float32]] = wd.to_dict()
                means[v] = {node_id: np.mean(ser) for node_id, ser in node_series.items()}

            print(means)

    @unittest.skipUnless(os.getenv("WEATHER_LONG_TESTS", False), "Long running")
    def test_generate_climate_readme_example(self):
        out_dir = str(self.test_dir)
        self._generate_climate_readme_example(out_dir=out_dir)

    @unittest.skipUnless(os.getenv("WEATHER_LONG_TESTS", False), "Long running")
    def test_generate_climate_readme_example_other_data_source1(self):
        self._generate_climate_readme_example(data_source="ERA5-LAND")

    @unittest.skipUnless(os.getenv("WEATHER_LONG_TESTS", False), "Long running")
    def test_generate_climate_readme_example_other_data_source2(self):
        self._generate_climate_readme_example(data_source="TAMSATv3")

    def _generate_climate_readme_example(self, data_source: str = None, out_dir: str = None):
        """See emodpy-malaria/emodpy_malaria/weather/README.md"""
        # Specify arguments
        start_year, end_year = 2015001, 2015003     # Shorter than in example
        site_csv = self.sites_africa_csv if data_source == "TAMSATv3" else self.sites_csv

        assert Path(site_csv).is_file()

        # Request weather files
        wr: WeatherRequest = generate_weather(platform="Bayesian",
                                              site_file=site_csv,
                                              start_date=start_year,
                                              end_date=end_year,
                                              node_column="id",
                                              local_dir=out_dir,
                                              data_source=data_source)

        print(f"Weather asset collection id: {wr.data_id}")
        print(f"Files are downloaded in dir: {wr.local_dir}")  # same as out_dir

        if out_dir:
            self.assertEqual(wr.local_dir, out_dir)

        if wr.files_exist:
            print("Downloaded files:")
            print(wr.files)
        else:
            print(f"Oops...")
            print(wr.report.download)

        # Load and convert to a dataframe
        ws = WeatherSet.from_files(dir_path=wr.local_dir)
        df = ws.to_dataframe()
        self.assertTrue(len(df) > 0)


if __name__ == '__main__':
    unittest.main()
