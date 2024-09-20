import os

#
# This is a user-modifiable Python file designed to be a set of simple input file and directory settings that you can choose and change.
#
# the location of the file containing AssetCollection id for the dtk sif (singularity image)
sif_path = os.path.join(os.pardir, 'dtk_sif.id')
# Path to experiment id of experiment that created the serialized population 
experiment_id = "../burnin_create_infections/experiment_id"
eradication_path="download/Eradication"
schema_file="download/schema.json"
plugins_folder = "download/reporter_plugins"

# Path to serialized population that was saved by eradication
source = "state-00050.dtk"
ser_path = "../burnin_create_infections/serialization_files/output"
ser_out_path = "output"

# Output file without human and vector infections
destination = "state-00050_zeroed.dtk"

# Create 'Assets' directory or change to a path you prefer. idmtools will upload files found here.
assets_input_dir="Assets"



