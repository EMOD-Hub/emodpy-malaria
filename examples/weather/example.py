from pathlib import Path
from emodpy import emod_task
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

if __name__ == "__main__":
    exp_name = "ERA5 data testing"
    input_dir = Path(__file__).parent.joinpath('input')
    print(input_dir)
    cb = emod_task.EMODTask.from_files(config_path=str(Path(input_dir).joinpath('config.json')),
                                       campaign_path=str(Path(input_dir).joinpath('campaign.json')),
                                       eradication_path=str(Path(input_dir).joinpath('Eradication')))
    cb.common_assets.add_asset(str(Path(__file__).parent.joinpath('input/demographics.json')))
    cb.common_assets.add_directory(str(Path(__file__).parent.joinpath('output/demo1')), relative_path="climate")
    cb.set_parameter('Simulation_Duration', 15)
    builder = SimulationBuilder()
    builder.add_sweep_definition(emod_task.EMODTask.set_parameter_partial("Run_Number"), range(0, 1))
    e = Experiment.from_builder(builder, cb, name=exp_name)
    #platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    platform = Platform("SLURMStage", num_retries=0)
    e.run(platform=platform, wait_until_done=True)
    assert (e.succeeded)
    with open('experiment_id', 'w') as f:
        f.write(str(e.id))
