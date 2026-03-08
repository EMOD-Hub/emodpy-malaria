import os

ep4_path="EP4"
schema_file="download/schema.json"
eradication_path="download/Eradication"
assets_input_dir="Assets"
plugins_folder="download"
reporters="download/reporter_plugins"

with open(os.path.join('..', 'image_name')) as fid01:
    image_str = fid01.readlines()[0].strip()

with open(os.path.join('..', 'image_name')) as fid01:
    image_str = fid01.readlines()[0].strip()

plat_name = "Container"
job_dir = "../example_jobs"
plat_image = image_str