import unittest
from functools import partial

import pytest

import emodpy.emod_task as emod_task
import emodpy_malaria.malaria_config as malaria_config
import emodpy_malaria.vector_config as vector_config
import emodpy_malaria.campaign.individual_intervention as ind
import emodpy_malaria.campaign.node_intervention as node_iv
import emodpy_malaria.campaign.distributor as distribute
import emodpy_malaria.campaign.waning_config as waning
import emodpy_malaria.campaign.event_coordinator as ec
from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
from emodpy_malaria.utils.emod_enum import VectorCountType, VectorGender, NucleotideSequenceOrigin, HabitatType
from emodpy_malaria.utils.distributions import ConstantDistribution
from emodpy_malaria.utils.targeting_config import IsPregnant

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import manifest


def _base_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])
    config.parameters.Simulation_Duration = 1
    config.parameters.Run_Number = 0
    return config


def _base_demog():
    return MalariaDemographics.from_template_node(pop=100)


@pytest.mark.unit
class TestInsecticideNameImplicit(unittest.TestCase):

    def _config_with_insecticide(self, config):
        config = _base_config(config)
        vector_config.add_insecticide_resistance(
            config, manifest, insecticide_name="pyrethroid", species="gambiae",
            allele_combo=[["X", "X"]], killing=0.5)
        return config

    def _campaign_with_bednet_insecticide(self, campaign, name):
        campaign.set_schema(manifest.schema_path)
        bednet = ind.SimpleBednet(
            campaign,
            blocking_config=waning.Constant(0.9),
            killing_config=waning.Constant(0.6),
            repelling_config=waning.Constant(0.0),
            insecticide_name=name,
        )
        distribute.add_intervention_scheduled(campaign, intervention_list=[bednet], start_day=0)
        return campaign

    def test_insecticide_name_valid_passes(self):
        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=self._config_with_insecticide,
            campaign_builder=partial(self._campaign_with_bednet_insecticide, name="pyrethroid"),
            demographics_builder=_base_demog,
        )

    def test_insecticide_name_invalid_raises(self):
        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=self._config_with_insecticide,
                campaign_builder=partial(self._campaign_with_bednet_insecticide, name="nonexistent"),
                demographics_builder=_base_demog,
            )
        self.assertIn("nonexistent", str(ctx.exception))
        self.assertIn("add_insecticide_resistance", str(ctx.exception))

    def test_insecticide_name_no_insecticides_configured_raises(self):
        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=_base_config,
                campaign_builder=partial(self._campaign_with_bednet_insecticide, name="pyrethroid"),
                demographics_builder=_base_demog,
            )
        self.assertIn("pyrethroid", str(ctx.exception))

    def test_insecticide_name_irs_valid_passes(self):
        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            irs = ind.IRSHousingModification(
                campaign,
                killing_config=waning.Constant(0.5),
                repelling_config=waning.Constant(0.3),
                insecticide_name="pyrethroid",
            )
            distribute.add_intervention_scheduled(campaign, intervention_list=[irs], start_day=0)
            return campaign

        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=self._config_with_insecticide,
            campaign_builder=campaign_fn,
            demographics_builder=_base_demog,
        )

    def test_insecticide_name_node_intervention_raises(self):
        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            spray = node_iv.SpaceSpraying(
                campaign,
                killing_config=waning.Constant(0.8),
                insecticide_name="bad_name",
            )
            distribute.add_intervention_scheduled(campaign, intervention_list=[spray], start_day=0)
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=self._config_with_insecticide,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("bad_name", str(ctx.exception))

    def test_insecticide_name_multi_insecticide_valid_passes(self):
        def config_fn(config):
            config = _base_config(config)
            vector_config.add_insecticide_resistance(
                config, manifest, insecticide_name="pyrethroid", species="gambiae",
                allele_combo=[["X", "X"]], killing=0.5)
            vector_config.add_insecticide_resistance(
                config, manifest, insecticide_name="organophosphate", species="gambiae",
                allele_combo=[["X", "X"]], killing=0.3)
            return config

        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            ins1 = waning.InsecticideWaningEffect(
                campaign, killing_config=waning.Constant(0.8), insecticide_name="pyrethroid")
            ins2 = waning.InsecticideWaningEffect(
                campaign, killing_config=waning.Constant(0.6), insecticide_name="organophosphate")
            spray = node_iv.MultiInsecticideSpaceSpraying(
                campaign, insecticides=[ins1, ins2])
            distribute.add_intervention_scheduled(campaign, intervention_list=[spray], start_day=0)
            return campaign

        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=config_fn,
            campaign_builder=campaign_fn,
            demographics_builder=_base_demog,
        )

    def test_insecticide_name_multi_insecticide_invalid_raises(self):
        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            ins1 = waning.InsecticideWaningEffect(
                campaign, killing_config=waning.Constant(0.8), insecticide_name="pyrethroid")
            ins2 = waning.InsecticideWaningEffect(
                campaign, killing_config=waning.Constant(0.6), insecticide_name="does_not_exist")
            spray = node_iv.MultiInsecticideSpaceSpraying(
                campaign, insecticides=[ins1, ins2])
            distribute.add_intervention_scheduled(campaign, intervention_list=[spray], start_day=0)
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=self._config_with_insecticide,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("does_not_exist", str(ctx.exception))


@pytest.mark.unit
class TestVectorSamplingTypeImplicit(unittest.TestCase):

    def test_oviposition_trap_valid_passes(self):
        def config_fn(config):
            config = _base_config(config)
            config.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
            return config

        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            trap = node_iv.OvipositionTrap(
                campaign, killing_config=waning.Constant(0.5))
            distribute.add_intervention_scheduled(campaign, intervention_list=[trap], start_day=0)
            return campaign

        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=config_fn,
            campaign_builder=campaign_fn,
            demographics_builder=_base_demog,
        )

    def test_oviposition_trap_invalid_raises(self):
        def config_fn(config):
            config = _base_config(config)
            config.parameters.Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
            return config

        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            trap = node_iv.OvipositionTrap(
                campaign, killing_config=waning.Constant(0.5))
            distribute.add_intervention_scheduled(campaign, intervention_list=[trap], start_day=0)
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=config_fn,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("Vector_Sampling_Type", str(ctx.exception))
        self.assertIn("TRACK_ALL_VECTORS", str(ctx.exception))

    def test_vector_surveillance_invalid_raises(self):
        def config_fn(config):
            config = _base_config(config)
            config.parameters.Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
            return config

        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            counter = ec.VectorCounter(
                species="gambiae",
                sample_size_distribution=ConstantDistribution(100),
                count_type=VectorCountType.ALLELE_FREQ,
                gender=VectorGender.VECTOR_FEMALE,
                update_period=30,
            )
            broadcast = node_iv.BroadcastCoordinatorEventFromNode(
                campaign, broadcast_event="StartSurveillance")
            distribute.add_intervention_scheduled(
                campaign, intervention_list=[broadcast], start_day=0)
            ec.VectorSurveillanceEventCoordinator(
                campaign, counter=counter,
                start_trigger_condition_list=["StartSurveillance"],
            )
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=config_fn,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("Vector_Sampling_Type", str(ctx.exception))


@pytest.mark.unit
class TestSugarFeedingImplicit(unittest.TestCase):

    def test_sugar_trap_valid_passes(self):
        def config_fn(config):
            config = _base_config(config)
            config.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
            for sp in config.parameters.Vector_Species_Params:
                sp.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_EVERY_FEED"
            return config

        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            trap = node_iv.SugarTrap(
                campaign, killing_config=waning.Constant(0.5))
            distribute.add_intervention_scheduled(campaign, intervention_list=[trap], start_day=0)
            return campaign

        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=config_fn,
            campaign_builder=campaign_fn,
            demographics_builder=_base_demog,
        )

    def test_sugar_trap_no_feeding_raises(self):
        def config_fn(config):
            config = _base_config(config)
            config.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
            return config

        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            trap = node_iv.SugarTrap(
                campaign, killing_config=waning.Constant(0.5))
            distribute.add_intervention_scheduled(campaign, intervention_list=[trap], start_day=0)
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=config_fn,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("Vector_Sugar_Feeding_Frequency", str(ctx.exception))


@pytest.mark.unit
class TestMalariaModelImplicit(unittest.TestCase):

    def test_outbreak_genetics_invalid_raises(self):
        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            ob = ind.OutbreakIndividualMalariaGenetics(
                campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
                barcode_string="AATTCCGG")
            distribute.add_intervention_scheduled(campaign, intervention_list=[ob], start_day=0)
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=_base_config,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("Malaria_Model", str(ctx.exception))
        self.assertIn("MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS", str(ctx.exception))


@pytest.mark.unit
class TestBirthRateDependenceImplicit(unittest.TestCase):

    def test_is_pregnant_valid_passes(self):
        def config_fn(config):
            config = _base_config(config)
            config.parameters.Birth_Rate_Dependence = "INDIVIDUAL_PREGNANCIES"
            return config

        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            ob = ind.OutbreakIndividual(campaign)
            distribute.add_intervention_scheduled(
                campaign, intervention_list=[ob], start_day=0,
                targeting_config=IsPregnant())
            return campaign

        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=config_fn,
            campaign_builder=campaign_fn,
            demographics_builder=_base_demog,
        )

    def test_is_pregnant_wrong_dependence_raises(self):
        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            ob = ind.OutbreakIndividual(campaign)
            distribute.add_intervention_scheduled(
                campaign, intervention_list=[ob], start_day=0,
                targeting_config=IsPregnant())
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=_base_config,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("Birth_Rate_Dependence", str(ctx.exception))


@pytest.mark.unit
class TestLarvalHabitatImplicit(unittest.TestCase):

    def _campaign_with_scale_larval_habitat(self, campaign, habitat, species="ALL_SPECIES"):
        campaign.set_schema(manifest.schema_path)
        spec = node_iv.LarvalHabitatMultiplierSpec(
            campaign, habitat=habitat, factor=1.5, species=species)
        iv = node_iv.ScaleLarvalHabitat(campaign, larval_habitat_multiplier=[spec])
        distribute.add_intervention_scheduled(campaign, intervention_list=[iv], start_day=0)
        return campaign

    def test_valid_habitat_for_species_passes(self):
        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=_base_config,
            campaign_builder=partial(
                self._campaign_with_scale_larval_habitat,
                habitat=HabitatType.WATER_VEGETATION,
                species="gambiae",
            ),
            demographics_builder=_base_demog,
        )

    def test_all_habitats_always_passes(self):
        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=_base_config,
            campaign_builder=partial(
                self._campaign_with_scale_larval_habitat,
                habitat=HabitatType.ALL_HABITATS,
            ),
            demographics_builder=_base_demog,
        )

    def test_wrong_habitat_for_species_raises(self):
        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=_base_config,
                campaign_builder=partial(
                    self._campaign_with_scale_larval_habitat,
                    habitat=HabitatType.TEMPORARY_RAINFALL,
                    species="gambiae",
                ),
                demographics_builder=_base_demog,
            )
        self.assertIn("TEMPORARY_RAINFALL", str(ctx.exception))

    def test_species_not_in_config_raises(self):
        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=_base_config,
                campaign_builder=partial(
                    self._campaign_with_scale_larval_habitat,
                    habitat=HabitatType.WATER_VEGETATION,
                    species="arabiensis",
                ),
                demographics_builder=_base_demog,
            )
        self.assertIn("arabiensis", str(ctx.exception))


@pytest.mark.unit
class TestMosquitoReleaseGenomeImplicit(unittest.TestCase):

    def _config_with_gambiae_gene(self, config):
        config = _base_config(config)
        # One autosomal gene, no explicit gender gene → expected loci = 2 (implicit gender + 1 gene)
        vector_config.add_genes_and_alleles(
            config, manifest, "gambiae", [("a1", 0.5), ("a2", 0.5)])
        return config

    def _campaign_with_release(self, campaign, species, genome):
        campaign.set_schema(manifest.schema_path)
        release = node_iv.MosquitoRelease(
            campaign,
            released_species=species,
            released_genome=genome,
            released_number=1000,
        )
        distribute.add_intervention_scheduled(campaign, intervention_list=[release], start_day=0)
        return campaign

    def test_valid_genome_passes(self):
        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=self._config_with_gambiae_gene,
            campaign_builder=partial(
                self._campaign_with_release,
                species="gambiae",
                genome=[["X", "X"], ["a1", "a1"]],
            ),
            demographics_builder=_base_demog,
        )

    def test_species_not_in_config_raises(self):
        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=self._config_with_gambiae_gene,
                campaign_builder=partial(
                    self._campaign_with_release,
                    species="funestus",
                    genome=[["X", "X"], ["a1", "a1"]],
                ),
                demographics_builder=_base_demog,
            )
        self.assertIn("funestus", str(ctx.exception))

    def test_wrong_locus_count_raises(self):
        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=self._config_with_gambiae_gene,
                campaign_builder=partial(
                    self._campaign_with_release,
                    species="gambiae",
                    genome=[["X", "X"]],  # 1 locus, expected 2
                ),
                demographics_builder=_base_demog,
            )
        self.assertIn("loci", str(ctx.exception))

    def test_invalid_allele_name_raises(self):
        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=self._config_with_gambiae_gene,
                campaign_builder=partial(
                    self._campaign_with_release,
                    species="gambiae",
                    genome=[["X", "X"], ["bad_allele", "a1"]],
                ),
                demographics_builder=_base_demog,
            )
        self.assertIn("bad_allele", str(ctx.exception))


@pytest.mark.unit
class TestGenomeLocationsLengthImplicit(unittest.TestCase):

    def _genetics_config(self, config):
        malaria_config.set_parasite_genetics_params(config, manifest)
        config.parameters.Simulation_Duration = 1
        config.parameters.Run_Number = 0
        return config

    def test_barcode_string_wrong_length_raises(self):
        # set_parasite_genetics_params sets 24 Barcode_Genome_Locations by default
        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            ob = ind.OutbreakIndividualMalariaGenetics(
                campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
                barcode_string="ACGT",  # 4 chars, expected 24
            )
            distribute.add_intervention_scheduled(campaign, intervention_list=[ob], start_day=0)
            return campaign

        with self.assertRaises(ValueError) as ctx:
            emod_task.EMODTask.from_defaults(
                eradication_path=manifest.eradication_path,
                schema_path=manifest.schema_path,
                config_builder=self._genetics_config,
                campaign_builder=campaign_fn,
                demographics_builder=_base_demog,
            )
        self.assertIn("barcode_string", str(ctx.exception))
        self.assertIn("Barcode_Genome_Locations", str(ctx.exception))

    def test_barcode_string_correct_length_passes(self):
        # 24 chars matches 24 Barcode_Genome_Locations entries
        def campaign_fn(campaign):
            campaign.set_schema(manifest.schema_path)
            ob = ind.OutbreakIndividualMalariaGenetics(
                campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
                barcode_string="A" * 24,
            )
            distribute.add_intervention_scheduled(campaign, intervention_list=[ob], start_day=0)
            return campaign

        emod_task.EMODTask.from_defaults(
            eradication_path=manifest.eradication_path,
            schema_path=manifest.schema_path,
            config_builder=self._genetics_config,
            campaign_builder=campaign_fn,
            demographics_builder=_base_demog,
        )


if __name__ == "__main__":
    unittest.main()
