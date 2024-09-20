import os.path as path
current_directory = path.dirname(path.realpath(__file__))
schema_file = path.join(current_directory, "old_schemas", "latest_schema.json")
schema_path = schema_file