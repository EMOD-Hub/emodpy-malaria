import os

# The script is going to use this to store the downloaded schema file. Create 'download' directory or change to your preferred (existing) location.
schema_file="download/schema.json"

# The script is going to use this to store the downloaded Eradication binary. Create 'download' directory or change to your preferred (existing) location.
eradication_path="download/Eradication"

# Create 'Assets' directory or change to a path you prefer. idmtools will upload files found here.
assets_input_dir="Assets"
plugins_folder = "download/reporter_plugins"

my_ep4_assets=None

plat_name = "Container"
job_dir = "../example_jobs"
plat_image = "ghcr.io/institutefordiseasemodeling/container-rocky-runtime:0.0.6"
