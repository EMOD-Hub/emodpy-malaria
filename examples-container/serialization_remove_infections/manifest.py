import os

# Path to experiment id of experiment that created the serialized population 
experiment_id = "../burnin_create_infections/experiment_id"
eradication_path="download/Eradication"
schema_file="download/schema.json"
plugins_folder = "download/reporter_plugins"

# Path to serialized population that was saved by eradication
source = "state-00050.dtk"
ser_path = "../burnin_create_infections"
ser_out_path = "output"

# Output file without human and vector infections
destination = "state-00050_zeroed.dtk"

# Create 'Assets' directory or change to a path you prefer. idmtools will upload files found here.
assets_input_dir="Assets"

with open(os.path.join('..', 'image_name')) as fid01:
    image_str = fid01.readlines()[0].strip()

plat_name = "Container"
job_dir = "../example_jobs"
plat_image = image_str
