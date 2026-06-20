import pytest


@pytest.mark.unit
class TestImport:
    def test_import_package(self):
        import emodpy_malaria
        assert emodpy_malaria.__version__ == "6.0.0"

    def test_import_campaign_individual(self):
        from emodpy_malaria.campaign import individual_intervention
        assert hasattr(individual_intervention, 'AntimalarialDrug')
        assert hasattr(individual_intervention, 'SimpleBednet')
        assert hasattr(individual_intervention, 'MalariaDiagnostic')
        assert hasattr(individual_intervention, 'RTSSVaccine')
        assert hasattr(individual_intervention, 'AdherentDrug')
        assert hasattr(individual_intervention, 'Ivermectin')
        assert hasattr(individual_intervention, 'BroadcastEvent')
        assert hasattr(individual_intervention, 'SimpleVaccine')

    def test_import_campaign_node(self):
        from emodpy_malaria.campaign import node_intervention
        assert hasattr(node_intervention, 'SpaceSpraying')
        assert hasattr(node_intervention, 'Larvicides')
        assert hasattr(node_intervention, 'MosquitoRelease')
        assert hasattr(node_intervention, 'InputEIR')
        assert hasattr(node_intervention, 'ScaleLarvalHabitat')
        assert hasattr(node_intervention, 'LarvalMicrosporidiaIntervention')
        assert hasattr(node_intervention, 'MultiNodeInterventionDistributor')
        assert hasattr(node_intervention, 'Outbreak')

    def test_import_reporters(self):
        from emodpy_malaria.reporters import reporters
        assert hasattr(reporters, 'MalariaSummaryReport')
        assert hasattr(reporters, 'ReportVectorGenetics')
        assert hasattr(reporters, 'ReportVectorStats')
        assert hasattr(reporters, 'ReportMalariaFiltered')
        assert hasattr(reporters, 'MalariaImmunityReport')
        assert hasattr(reporters, 'ReportMicrosporidia')
        assert hasattr(reporters, 'InsetChart')
        assert hasattr(reporters, 'ReportEventCounter')

    def test_import_demographics(self):
        from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
        assert MalariaDemographics is not None

    def test_import_enums(self):
        from emodpy_malaria.utils.emod_enum import (
            DiagnosticType, HabitatType, VectorGender,
            EventOrConfig, ChallengeType, NucleotideSequenceOrigin,
            InputEIRAgeDependence, NonAdherenceOption,
        )
        assert DiagnosticType.BLOOD_SMEAR_PARASITES == "BLOOD_SMEAR_PARASITES"
        assert HabitatType.ALL_HABITATS == "ALL_HABITATS"
        assert VectorGender.VECTOR_FEMALE == "VECTOR_FEMALE"
        assert EventOrConfig.Event == "Event"
        assert EventOrConfig.Config == "Config"
        assert ChallengeType.INFECTIOUS_BITES == "InfectiousBites"
        assert ChallengeType.SPOROZOITES == "Sporozoites"
        assert NucleotideSequenceOrigin.BARCODE_STRING == "BARCODE_STRING"
        assert InputEIRAgeDependence.OFF == "OFF"
        assert NonAdherenceOption.STOP == "STOP"

    def test_import_distributor(self):
        from emodpy_malaria.campaign.distributor import add_intervention_scheduled, add_intervention_triggered
        assert callable(add_intervention_scheduled)
        assert callable(add_intervention_triggered)

    def test_import_waning_config(self):
        from emodpy_malaria.campaign.waning_config import Box, Constant, Exponential, BoxExponential
        assert Box is not None
        assert Constant is not None

    def test_import_event_coordinators(self):
        from emodpy_malaria.campaign.event_coordinator import (
            StandardEventCoordinator,
            VectorSurveillanceEventCoordinator,
            CommunityHealthWorkerEventCoordinator,
        )
        assert StandardEventCoordinator is not None
