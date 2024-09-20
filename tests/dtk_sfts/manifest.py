import os

#
# This is a user-modifiable Python file designed to be a set of simple input file and
# directory settings that you can choose and change.

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
SIF_DIR = os.path.join(CURRENT_DIR, "sif")
eradication_path = os.path.join("download", "Eradication")
schema_file = os.path.join("download", "schema.json")

ep4_dir = "ep4_dir"
input_folder = "download"
build_sif = os.path.join(SIF_DIR, "CentOS_8_Py39_Build.def")
build_id = os.path.join(SIF_DIR, "CentOS_8_Py39_Build.id")
eradication_ac = os.path.join(CURRENT_DIR, "EMOD_ac.id")
eradication_ac_38 = os.path.join(CURRENT_DIR, "EMOD_ac_38.id")

sft_sif = os.path.join(SIF_DIR, "CentOS_8_Py39_SFT.def")
sft_id = os.path.join(SIF_DIR, "CentOS_8_Py39_SFT.id")
exp_id = os.path.join(CURRENT_DIR, "experiments.id")

platform = 'SLURMStage'
config_path = 'config.json'
n_sims = 10
