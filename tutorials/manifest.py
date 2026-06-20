import os

tutorials_dir = os.path.dirname(__file__)

executables_dir = os.path.join(tutorials_dir, "executables")
schema_path = os.path.join(executables_dir, "schema.json")
schema_file = schema_path
eradication_path = os.path.join(executables_dir, "Eradication")

assets_input_dir = "Assets"

plat_image = "ghcr.io/emod-hub/emod-ubuntu-runtime:latest"
job_dir = os.path.join(tutorials_dir, "tutorial_output")

x_Base_Population_scale = 1
n_calibration_samples = 10
n_calibration_iterations = 5
burnin_serialize_years = 50

comps_sif_path = os.path.join(tutorials_dir, "comps_sif_file.id")
slurm_sif_path = "/path/to/emod-malaria.sif"
