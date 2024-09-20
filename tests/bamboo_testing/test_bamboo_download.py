import unittest
import os

from emodpy.utils import download_latest_schema, download_latest_eradication, \
    download_latest_reporters, EradicationBambooBuilds, bamboo_api_login, download_from_url
from emodpy.bamboo import get_model_files
import emodpy.bamboo_api_utils as bamboo_api

# Change for type of schema and Eradication
plan = EradicationBambooBuilds.MALARIA_LINUX

class TestBambooDownload(unittest.TestCase):
    def define_test_environment(self):
        self.plan = plan
        current_directory = os.path.dirname(os.path.realpath(__file__))
        self.eradication_path = os.path.join(current_directory , "./inputs/bin/Eradication")
        self.schema_path = os.path.join(current_directory , "./inputs/bin/schema.json")

    def setUp(self) -> None:
        self.define_test_environment()
        print('login to bamboo...')
        bamboo_api_login()

    def test_get_eradication(self):
        if os.path.isfile(self.eradication_path):
            os.remove(self.eradication_path)
        download_latest_eradication(
            plan=self.plan, scheduled_builds_only=False, out_path=self.eradication_path
        )
        self.assertTrue(os.path.isfile(self.eradication_path), msg=f'{self.eradication_path} does not exist.')

    def test_get_schema(self):
        if os.path.isfile(self.schema_path):
            os.remove(self.schema_path)
        download_latest_schema(
            plan=self.plan, scheduled_builds_only=False, out_path=self.schema_path
        )
        self.assertTrue(os.path.isfile(self.schema_path), msg=f'{self.schema_path} does not exist.')

if __name__ == "__main__":
    unittest.main()