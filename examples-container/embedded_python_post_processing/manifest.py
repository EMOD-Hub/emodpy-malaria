import os

# the location of the file containing AssetCollection id for the dtk sif (singularity image)
sif_id = os.path.join(os.pardir, '..', 'examples', 'dtk_sif.id')
ep4_path="EP4"
requirements = "./requirements.txt"
schema_file="download/schema.json"
eradication_path="download/Eradication"
assets_input_dir="Assets"
plugins_folder="download"
reporters="download/reporter_plugins"
sif="dtk_centos.id"

