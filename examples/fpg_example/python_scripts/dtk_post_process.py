import os

from fpg_observational_model.run_observational_model import run_observational_model


def application( output_path="output" ):
    # Example of a config dict that overrides defaults, please see all_config_dict above for all options
    overlay_config_dict = {
        'sampling_configs': {
            'random': {
                'n_samples_year': 20
            }
        },
        'metrics': {
            'identity_by_state': False
        },
        'subpopulation_comparisons': {
            'age_bins': True     # Default age bins: 0-5, 5-15, 15+
        }
    }

    run_observational_model(
        sim_name="fpg_sim",
        emod_output_path=output_path,
        config_path=None,
        config=overlay_config_dict,
        output_path=os.path.join(output_path, 'ObsModel_output'),
        verbose=True)

if __name__ == "__main__":
    application( "output" )
