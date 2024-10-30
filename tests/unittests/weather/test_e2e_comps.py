import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import numpy as np
import pandas
import numpy
from pathlib import Path

import pandas as pd
from emodpy_malaria.weather import *


class WeatherE2ECompsTests(unittest.TestCase):
    testfiles_dir = Path(__file__).parent.joinpath("scenarios")

    def setUp(self) -> None:
        # Login to comps
        self.comps_url = os.environ.get("COMPS_URL")
        self.comps_user = os.environ.get("COMPS_USER")
        self.comps_pass = os.environ.get("COMPS_PASS")
        if not self.comps_url or not self.comps_user or not self.comps_pass:
            print("Enter the credentials when prompt.")
        else:
            subprocess.run([sys.executable, Path(__file__).parent.parent.parent.joinpath("create_auth_token_args.py"),
                        "--comps_url", self.comps_url, "--username",  self.comps_user, "--password",  self.comps_pass])
        self.out_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.out_dir, ignore_errors=True)

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_request_weather(self):
        # Request weather files
        for ds in ['ERA5', 'ERA5-LAND', 'TAMSATv3']:
            site_csv = self.testfiles_dir.parent.joinpath("ssmt/sites.csv")
            start_year, end_year = 2020365, 2021001
            if ds == 'TAMSATv3':
                # only available in Africa
                site_csv = self.testfiles_dir.parent.joinpath("ssmt/sites_af.csv")
                start_year, end_year = 2016365, 2017001
            wr: WeatherRequest = generate_weather(platform="Calculon",
                                                  site_file=site_csv,
                                                  start_date=start_year,
                                                  end_date=end_year,
                                                  node_column="nodes",
                                                  lat_column="lat",
                                                  lon_column="lon",
                                                  local_dir=Path(self.out_dir).joinpath(ds),
                                                  request_name=f"test_request_emodpy_malaria_weather_{ds}",
                                                  data_source=ds)

            print(f"Weather asset collection id: {wr.data_id}")
            print(f"Files are downloaded in dir: {wr.local_dir}")
            assert Path(wr.local_dir) == Path(self.out_dir).joinpath(ds)
            # Check data
            ws: WeatherSet = WeatherSet.from_files(Path(self.out_dir).joinpath(ds))
            df = ws.to_dataframe()
            df_sites = pd.read_csv(site_csv)
            assert set(df.nodes.values) == set(df_sites.nodes.values)

    @unittest.skipIf(os.environ.get('ignore_comps', False), 'This is a comps dependent test')
    def test_request_weather_force(self):
        # place files in the output dir
        src_dir = self.testfiles_dir.parent.joinpath("case_default_names_all")
        shutil.copytree(str(src_dir), self.out_dir, dirs_exist_ok=True)

        one_file = Path(self.out_dir).joinpath('dtk_15arcmin_air_temperature_daily.bin')
        init_mtime = one_file.stat().st_mtime

        # Request weather files 1st time
        site_csv = self.testfiles_dir.parent.joinpath("ssmt/sites.csv")
        start_year, end_year = 2020365, 2021001

        wr1 = generate_weather(platform="Calculon",
                               site_file=site_csv,
                               start_date=start_year,
                               end_date=end_year,
                               node_column="nodes",
                               lat_column="lat",
                               lon_column="lon",
                               local_dir=Path(self.out_dir),
                               request_name=f"test_request_emodpy_malaria_weather_force",
                               force=False)

        self.assertEqual(len(wr1.report.download["ok"]), 0)
        self.assertEqual(len(wr1.report.download["skip"]), 8)

        wr2 = generate_weather(platform="Calculon",
                               site_file=site_csv,
                               start_date=start_year,
                               end_date=end_year,
                               node_column="nodes",
                               lat_column="lat",
                               lon_column="lon",
                               local_dir=Path(self.out_dir),
                               request_name=f"test_request_emodpy_malaria_weather_force",
                               force=True)

        self.assertEqual(len(wr2.report.download["ok"]), 8)
        self.assertEqual(len(wr2.report.download["skip"]), 0)

        self.assertGreater(one_file.stat().st_mtime, init_mtime)
