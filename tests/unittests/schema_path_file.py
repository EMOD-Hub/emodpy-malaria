import os.path as path
import emod_malaria.bootstrap as dtk

current_directory = path.dirname(path.realpath(__file__))
dtk.setup(path.join(current_directory, "current_schema"))
schema_file = path.join(current_directory, "current_schema", "schema.json")
