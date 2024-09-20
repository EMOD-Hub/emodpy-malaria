import unittest

class MalariaTestImports(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_items = None
        self.found_items = None
        pass

    def verify_expected_items_present(self, namespace):
        self.found_items = dir(namespace)
        for item in self.expected_items:
            self.assertIn(
                item,
                self.found_items
            )

    def tearDown(self) -> None:
        pass

    def test_requirements(self):
        import emod_api
        import emodpy_malaria
        import emodpy
        # Testing that we can import all requirements
        checks = [dir(package) for package in [emod_api, emodpy_malaria, emodpy]]
        for package in checks:
            self.assertIn('__package__', package)
        return

    # region interventions
    def test_intervention_bednet(self):
        from emodpy_malaria.interventions import bednet

        self.expected_items = [
            "Bednet", "BasicBednet", "utils"
        ]
        self.verify_expected_items_present(namespace=bednet)
        return

    def test_intervention_drug(self):
        from emodpy_malaria.interventions import drug

        self.expected_items = [
            "AntimalarialDrug", "utils"
        ]
        self.verify_expected_items_present(namespace=drug)
        return

    def test_intervention_irs(self):
        from emodpy_malaria.interventions import irs

        self.expected_items = [
            "add_irs_housing_modification", "utils"
        ]
        self.verify_expected_items_present(namespace=irs)
        return

    def test_intervention_outdoorrestkill(self):
        from emodpy_malaria.interventions import outdoorrestkill

        self.expected_items = [
            "add_OutdoorRestKill"
        ]
        self.verify_expected_items_present(namespace=outdoorrestkill)
        return

    def test_intervention_spacespraying(self):
        from emodpy_malaria.interventions import spacespraying

        self.expected_items = [
            "SpaceSpraying", "utils"
        ]

        self.verify_expected_items_present(namespace=spacespraying)
        return

    def test_intervention_sugartrap(self):
        from emodpy_malaria.interventions import sugartrap
        self.expected_items = [
            "SugarTrap", "utils"
        ]
        self.verify_expected_items_present(namespace=sugartrap)

    def test_intervention_udbednet(self):
        from emodpy_malaria.interventions import udbednet
        self.expected_items = [
            "UDBednet", "_get_seasonal_times_and_values", "_get_age_times_and_values"
        ]
        self.verify_expected_items_present(namespace=udbednet)

    def test_drug_campaign(self):
        from emodpy_malaria.interventions import drug_campaign
        self.expected_items = [
            "add_MDA", "add_MSAT",
            "add_drug_campaign", "add_fMDA",
            "add_rfMDA", "add_rfMSAT", "drug_configs_from_code",
            "fmda_cfg"
        ]
        self.verify_expected_items_present(namespace=drug_campaign)

    def test_ivermectin(self):
        from emodpy_malaria.interventions import ivermectin
        self.expected_items = [
            "Ivermectin"
        ]
        self.verify_expected_items_present(namespace=ivermectin)

    def test_diagnostic_survey(self):
        from emodpy_malaria.interventions import diag_survey
        self.expected_items = [
            "add_diagnostic_survey"
        ]
        self.verify_expected_items_present(namespace=diag_survey)

    def test_common_imports(self):
        from emodpy_malaria.interventions import common
        self.expected_items = [
            "AntimalarialDrug", "MalariaDiagnostic"
        ]

        self.verify_expected_items_present(namespace=common)

    # endregion

    # region demographics
    def test_demographics_imports(self):
        import emodpy_malaria.demographics.MalariaDemographics as Demographics

        self.expected_items = [
            "from_pop_csv", "from_template_node", "from_params"
        ]
        self.verify_expected_items_present(namespace=Demographics)

    # endregion

    # region config
    def test_config_imports(self):
        import emodpy_malaria.malaria_config as conf

        self.expected_items = [
            "get_file_from_http", "set_team_defaults",
            "set_team_drug_params", "set_parasite_genetics_params",
            "get_drug_params", "set_drug_param", "add_drug_resistance",
            "set_species_param", "add_insecticide_resistance"
        ]

        self.verify_expected_items_present(namespace=conf)

    def test_config_imports2(self):
        import emodpy_malaria.vector_config as conf

        self.expected_items = [
            "set_team_defaults",
            "get_species_params", "set_species_param",
            "add_species", "add_genes_and_alleles", "add_mutation",
            "add_trait", "add_insecticide_resistance", "add_species_drivers"
        ]

        self.verify_expected_items_present(namespace=conf)

    # endregion
