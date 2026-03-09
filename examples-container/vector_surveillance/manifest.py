import os

# The script is going to use this to store the downloaded schema file. Create 'download' directory or change to your preferred (existing) location.
schema_file = "download/schema.json"

# The script is going to use this to store the downloaded Eradication binary. Create 'download' directory or change to your preferred (existing) location.
eradication_path = "download/Eradication"

# Create 'Assets' directory or change to a path you prefer. idmtools will upload files found here.
assets_input_dir = "Assets"

plugins_folder = "download/reporter_plugins"

# python post- or pre-processing scripts directory
my_ep4_assets_dir = "ep4"

experiment_id = "experiment_id"

with open(os.path.join('..', 'image_name')) as fid01:
    image_str = fid01.readlines()[0].strip()

plat_name = "Container"
job_dir = "../example_jobs"
plat_image = image_str
