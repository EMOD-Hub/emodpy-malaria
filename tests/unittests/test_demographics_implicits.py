import os
import pathlib
import sys
import tempfile
import unittest
from functools import partial

import pandas as pd
import pytest

import emodpy.emod_task as emod_task
import emodpy_malaria.malaria_config as malaria_config
from emod_api.demographics.fertility_distribution import FertilityDistribution
from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
from emodpy_malaria.utils.distributions import UniformDistribution, ConstantDistribution
from emodpy_malaria.utils.emod_enum import ClimateUpdateResolution, InnateImmuneVariationType
from emodpy_malaria.weather.weather_set import WeatherSet
from emodpy_malaria.weather.weather_variable import WeatherVariable

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import manifest

_INVERSE = InnateImmuneVariationType.PYROGENIC_THRESHOLD_VS_AGE_INCREASING_AND_CYTOKINE_KILLING_INVERSE


def _base_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])
    config.parameters.Simulation_Duration = 1
    config.parameters.Run_Number = 0
    return config


def _make_task(demographics_builder):
    return emod_task.EMODTask.from_defaults(
        eradication_path=manifest.eradication_path,
        schema_path=manifest.schema_path,
        config_builder=_base_config,
        demographics_builder=demographics_builder,
    )


def _make_fertility_distribution():
    return FertilityDistribution(
        ages_years=[0.0, 15.0, 49.0],
        calendar_years=[2000.0, 2010.0],
        pregnancy_rate_matrix=[[0.01, 0.02], [0.05, 0.06], [0.01, 0.01]],
    )


def _make_weather_set(node_ids):
    rows = [
        {"node": nid, "step": step, "airtemp": 25.0, "humidity": 0.8, "rainfall": 5.0}
        for nid in node_ids
        for step in range(365)
    ]
    df = pd.DataFrame(rows)
    return WeatherSet.from_dataframe(
        df,
        node_column="node",
        step_column="step",
        weather_columns={
            WeatherVariable.AIR_TEMPERATURE: "airtemp",
            WeatherVariable.RELATIVE_HUMIDITY: "humidity",
            WeatherVariable.RAINFALL: "rainfall",
        },
    )


@pytest.mark.unit
class TestSetRiskDistributionImplicit(unittest.TestCase):

    def test_enable_demographics_risk_set(self):
        def demog():
            d = MalariaDemographics.from_template_node(pop=100)
            d.set_risk_distribution(UniformDistribution(0.5, 1.5))
            return d

        task = _make_task(demog)
        self.assertEqual(task.config.parameters.Enable_Demographics_Risk, 1)

    def test_enable_demographics_risk_not_set_without_distribution(self):
        def demog():
            return MalariaDemographics.from_template_node(pop=100)

        task = _make_task(demog)
        self.assertNotEqual(task.config.parameters.Enable_Demographics_Risk, 1)


@pytest.mark.unit
class TestSetInnateImmuneDistributionImplicit(unittest.TestCase):

    def _task_with_variation_type(self, variation_type, distribution=UniformDistribution(0.1, 0.9)):
        def demog():
            d = MalariaDemographics.from_template_node(pop=100)
            d.set_innate_immune_distribution(distribution, variation_type)
            return d
        return _make_task(demog)

    def test_pyrogenic_threshold(self):
        task = self._task_with_variation_type(InnateImmuneVariationType.PYROGENIC_THRESHOLD)
        self.assertEqual(
            task.config.parameters.Innate_Immune_Variation_Type,
            "PYROGENIC_THRESHOLD",
        )

    def test_cytokine_killing(self):
        task = self._task_with_variation_type(InnateImmuneVariationType.CYTOKINE_KILLING)
        self.assertEqual(
            task.config.parameters.Innate_Immune_Variation_Type,
            "CYTOKINE_KILLING",
        )

    def test_pyrogenic_threshold_vs_age_concave(self):
        task = self._task_with_variation_type(
            InnateImmuneVariationType.PYROGENIC_THRESHOLD_VS_AGE_CONCAVE
        )
        self.assertEqual(
            task.config.parameters.Innate_Immune_Variation_Type,
            "PYROGENIC_THRESHOLD_VS_AGE_CONCAVE",
        )

    def test_inverse_type_with_none_distribution(self):
        task = self._task_with_variation_type(_INVERSE, distribution=None)
        self.assertEqual(
            task.config.parameters.Innate_Immune_Variation_Type,
            _INVERSE.value,
        )


@pytest.mark.unit
class TestSetFertilityDistributionImplicit(unittest.TestCase):

    def test_birth_rate_dependence_set(self):
        def demog():
            d = MalariaDemographics.from_template_node(pop=100)
            d.set_fertility_distribution(_make_fertility_distribution())
            return d

        task = _make_task(demog)
        self.assertEqual(
            str(task.config.parameters.Birth_Rate_Dependence),
            "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR",
        )


@pytest.mark.unit
class TestSetPrevalenceDistributionImplicit(unittest.TestCase):

    def test_enable_initial_prevalence_set(self):
        def demog():
            d = MalariaDemographics.from_template_node(pop=100)
            d.set_prevalence_distribution(ConstantDistribution(0.1))
            return d

        task = _make_task(demog)
        self.assertEqual(task.config.parameters.Enable_Initial_Prevalence, 1)


@pytest.mark.unit
class TestAddWeatherImplicit(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._orig_cwd = os.getcwd()
        os.chdir(self._tmpdir)

    def tearDown(self):
        os.chdir(self._orig_cwd)

    def _make_task_with_weather(self, **weather_kwargs):
        ws = _make_weather_set([1])
        demog_obj = MalariaDemographics.from_template_node(pop=100, forced_id=1)
        demog_obj.add_weather(ws, **weather_kwargs)

        def demog():
            return demog_obj

        return _make_task(demog)

    def test_climate_model_set_to_climate_by_data(self):
        task = self._make_task_with_weather()
        self.assertEqual(str(task.config.parameters.Climate_Model), "CLIMATE_BY_DATA")

    def test_default_update_resolution(self):
        task = self._make_task_with_weather()
        self.assertEqual(
            str(task.config.parameters.Climate_Update_Resolution),
            "CLIMATE_UPDATE_DAY",
        )

    def test_monthly_update_resolution(self):
        task = self._make_task_with_weather(
            update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_MONTH
        )
        self.assertEqual(
            str(task.config.parameters.Climate_Update_Resolution),
            "CLIMATE_UPDATE_MONTH",
        )

    def test_air_temperature_filename_set(self):
        task = self._make_task_with_weather()
        self.assertIn("airtemp", task.config.parameters.Air_Temperature_Filename)

    def test_rainfall_filename_set(self):
        task = self._make_task_with_weather()
        self.assertIn("rainfall", task.config.parameters.Rainfall_Filename)

    def test_relative_humidity_filename_set(self):
        task = self._make_task_with_weather()
        self.assertIn("humidity", task.config.parameters.Relative_Humidity_Filename)

    def test_land_temperature_filename_mirrors_air_temperature(self):
        task = self._make_task_with_weather()
        self.assertEqual(
            task.config.parameters.Air_Temperature_Filename,
            task.config.parameters.Land_Temperature_Filename,
        )

    def test_air_temperature_offset(self):
        task = self._make_task_with_weather(air_temperature_offset=3.5)
        self.assertEqual(task.config.parameters.Air_Temperature_Offset, 3.5)

    def test_rainfall_scale_factor(self):
        task = self._make_task_with_weather(rainfall_scale_factor=1.5)
        self.assertEqual(task.config.parameters.Rainfall_Scale_Factor, 1.5)

    def test_relative_humidity_scale_factor(self):
        task = self._make_task_with_weather(relative_humidity_scale_factor=0.9)
        self.assertEqual(task.config.parameters.Relative_Humidity_Scale_Factor, 0.9)

    def test_climate_stochasticity_on_when_air_temperature_variance_nonzero(self):
        task = self._make_task_with_weather(air_temperature_variance=1.0)
        self.assertEqual(task.config.parameters.Enable_Climate_Stochasticity, 1)

    def test_climate_stochasticity_on_when_relative_humidity_variance_nonzero(self):
        task = self._make_task_with_weather(relative_humidity_variance=0.05)
        self.assertEqual(task.config.parameters.Enable_Climate_Stochasticity, 1)

    def test_rainfall_stochasticity_off_by_default(self):
        task = self._make_task_with_weather()
        self.assertEqual(task.config.parameters.Enable_Rainfall_Stochasticity, 0)

    def test_rainfall_stochasticity_on_when_enabled(self):
        task = self._make_task_with_weather(enable_rainfall_stochasticity=True)
        self.assertEqual(task.config.parameters.Enable_Rainfall_Stochasticity, 1)

    def test_climate_stochasticity_on_when_rainfall_stochasticity_enabled(self):
        task = self._make_task_with_weather(enable_rainfall_stochasticity=True)
        self.assertEqual(task.config.parameters.Enable_Climate_Stochasticity, 1)


@pytest.mark.unit
class TestSetMigrationHeterogeneityImplicit(unittest.TestCase):

    def _make_task_with_migration_heterogeneity(self, distribution):
        def demog():
            d = MalariaDemographics.from_template_node(pop=100)
            d.set_migration_heterogeneity(distribution)
            return d
        return _make_task(demog)

    def test_migration_model_set_to_fixed_rate(self):
        task = self._make_task_with_migration_heterogeneity(ConstantDistribution(1.0))
        self.assertEqual(str(task.config.parameters.Migration_Model), "FIXED_RATE_MIGRATION")

    def test_enable_migration_heterogeneity_set(self):
        task = self._make_task_with_migration_heterogeneity(UniformDistribution(0.5, 1.5))
        self.assertEqual(task.config.parameters.Enable_Migration_Heterogeneity, 1)


if __name__ == "__main__":
    unittest.main()
