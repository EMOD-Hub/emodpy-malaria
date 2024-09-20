import unittest
import os

from emodpy.utils import download_latest_schema, download_latest_eradication, \
    download_latest_reporters, EradicationBambooBuilds, bamboo_api_login, download_from_url
from emodpy.bamboo import get_model_files
import emodpy.bamboo_api_utils as bamboo_api

plan = EradicationBambooBuilds.MALARIA_LINUX
schema_path = os.path.join(current_directory , "./old_schemas/schema.json")

bamboo_api_login()
if os.path.isfile(schema_path):
    os.remove(schema_path)
download_latest_schema(
            plan=plan, scheduled_builds_only=False, out_path=schema_path
        )


