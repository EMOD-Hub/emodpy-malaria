import os

from idm_test.dtk_test.integration.integration_test import IntegrationTest
from idm_test.dtk_test.integration import bootstrap
import os
import sys
# using manifest from tests/dtk_sfts folder, will use it for all the malaria tests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manifest


def sweep_duration_to_disease(simulation, value):
    """
    The config parameter sweep function
    """
    simulation.task.config.parameters.Vector_Species_Params[0].Microsporidia_Duration_To_Disease_Acquisition_Modification.Times[1] = value
    return {"duration_to_disease": value}


def set_param_fn(config):
    """
    Update the config parameters from default values.
    """
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])
    config.parameters.Simulation_Duration = 700
    duration_to_disease_acquisition = {
        "Times": [0],
        "Values": [0]
    }
    malaria_config.add_microsporidia(config, manifest, species_name="gambiae",
                                     female_to_male_probability=1,
                                     male_to_female_probability=1, female_to_egg_probability=1,
                                     duration_to_disease_acquisition_modification=duration_to_disease_acquisition,
                                     larval_growth_modifier=1,
                                     female_mortality_modifier=0.5, male_mortality_modifier=0.5)

    config.parameters['Config_Name'] = 'test_microsporidia_duration_to_disease'
    config.parameters['Python_Script_Path'] = 'LOCAL'
    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    """
    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.mosquitorelease import add_scheduled_mosquito_release

    campaign.set_schema(manifest.schema_file)

    add_scheduled_mosquito_release(campaign, 50, released_number=10000, released_species="gambiae",
                                   released_microsopridia=True)
    return campaign


def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.demographics or emodpy_**disease**.demographics
    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=5000, name=1, forced_id=1)
    return demographics


class TestMicrosporidiaDisease(IntegrationTest):
    def setUp(self):
        # test_name is optional but recommended
        self.test_name = 'test_microsporidia_duration_to_disease_simple'
        # Copy Singularity definition files from idm_test package to your local folder(default value is './../sif').
        CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
        sif_dir = os.path.join(CURRENT_DIR, "..", "sif")
        bootstrap.setup(local_dir=sif_dir)

    def test_microsporidia_duration_to_disease(self):
        self.run_test(camp_fn_cb=build_camp, demog_fn_cb=build_demog, sweep_fn_cb=None,
                      sweep_values=None, manifest=manifest, set_param_fn=set_param_fn,
                      force_build_exe=False)


if __name__ == '__main__':
    import unittest
    unittest.main()
