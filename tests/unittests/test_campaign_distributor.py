import unittest
import pytest

from emod_api import campaign as api_campaign

from emodpy_malaria.campaign.distributor import add_vector_surveillance, add_broadcast_coordinator_event
from emodpy_malaria.campaign.event_coordinator import VectorCounter, VectorSurveillanceEventCoordinator
from emodpy_malaria.utils.distributions import ConstantDistribution, UniformDistribution
from emodpy_malaria.utils.emod_enum import VectorCountType, VectorGender

from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest  # noqa: E402


@pytest.mark.unit
class TestAddVectorSurveillance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_path = manifest.schema_path

    def setUp(self):
        self.campaign = api_campaign
        self.campaign.set_schema(self.schema_path)

    def _make_counter(self, **kwargs):
        defaults = dict(
            species="gambiae",
            sample_size_distribution=ConstantDistribution(100),
            count_type=VectorCountType.ALLELE_FREQ,
            gender=VectorGender.VECTOR_FEMALE,
            update_period=30,
        )
        defaults.update(kwargs)
        return VectorCounter(**defaults)

    def test_default(self):
        counter = self._make_counter()
        add_vector_surveillance(
            campaign=self.campaign,
            counter=counter,
            start_trigger_condition_list=["StartSurveillance"],
            start_day=1)

        self.assertEqual(len(self.campaign.campaign_dict['Events']), 1)
        event = self.campaign.campaign_dict['Events'][0]
        self.assertEqual(event['class'], 'CampaignEvent')
        self.assertEqual(event.Start_Day, 1)
        self.assertEqual(event.Nodeset_Config['class'], 'NodeSetAll')

        coordinator = event.Event_Coordinator_Config
        self.assertEqual(coordinator['class'], 'VectorSurveillanceEventCoordinator')
        self.assertEqual(coordinator.Start_Trigger_Condition_List, ["StartSurveillance"])
        self.assertEqual(coordinator.Counter.Species, "gambiae")
        self.assertEqual(coordinator.Counter.Count_Type, VectorCountType.ALLELE_FREQ)
        self.assertEqual(coordinator.Counter.Gender, VectorGender.VECTOR_FEMALE)
        self.assertEqual(coordinator.Counter.Update_Period, 30)

    def test_with_all_options(self):
        counter = self._make_counter(
            count_type=VectorCountType.GENOME_FRACTION,
            gender=VectorGender.VECTOR_BOTH_GENDERS,
            update_period=7)
        add_vector_surveillance(
            campaign=self.campaign,
            counter=counter,
            start_trigger_condition_list=["StartSurveillance", "ResumeSurveillance"],
            start_day=10,
            survey_completed_event="SurveyDone",
            duration=365,
            stop_trigger_condition_list=["StopSurveillance"],
            coordinator_name="MyVectorSurveillance",
            event_name="vector_surveillance_event",
            node_ids=[1, 2, 3])

        self.assertEqual(len(self.campaign.campaign_dict['Events']), 1)
        event = self.campaign.campaign_dict['Events'][0]
        self.assertEqual(event['class'], 'CampaignEvent')
        self.assertEqual(event.Start_Day, 10)
        self.assertEqual(event.Event_Name, "vector_surveillance_event")
        self.assertEqual(event.Nodeset_Config['class'], 'NodeSetNodeList')
        self.assertEqual(event.Nodeset_Config.Node_List, [1, 2, 3])

        coordinator = event.Event_Coordinator_Config
        self.assertEqual(coordinator['class'], 'VectorSurveillanceEventCoordinator')
        self.assertEqual(coordinator.Start_Trigger_Condition_List, ["StartSurveillance", "ResumeSurveillance"])
        self.assertEqual(coordinator.Stop_Trigger_Condition_List, ["StopSurveillance"])
        self.assertEqual(coordinator.Duration, 365)
        self.assertEqual(coordinator.Coordinator_Name, "MyVectorSurveillance")
        self.assertEqual(coordinator.Counter.Count_Type, VectorCountType.GENOME_FRACTION)
        self.assertEqual(coordinator.Counter.Gender, VectorGender.VECTOR_BOTH_GENDERS)
        self.assertEqual(coordinator.Counter.Update_Period, 7)

    def test_uniform_sample_size(self):
        counter = self._make_counter(sample_size_distribution=UniformDistribution(50, 200))
        add_vector_surveillance(
            campaign=self.campaign,
            counter=counter,
            start_trigger_condition_list=["StartSurveillance"],
            start_day=1)

        event = self.campaign.campaign_dict['Events'][0]
        coordinator = event.Event_Coordinator_Config
        self.assertEqual(coordinator['class'], 'VectorSurveillanceEventCoordinator')
        self.assertEqual(coordinator.Counter.Species, "gambiae")

    def test_empty_start_trigger_raises(self):
        counter = self._make_counter()
        with self.assertRaises(ValueError) as context:
            add_vector_surveillance(
                campaign=self.campaign,
                counter=counter,
                start_trigger_condition_list=[],
                start_day=1)
        self.assertIn("start_trigger_condition_list", str(context.exception))

    def test_invalid_counter_type_raises(self):
        with self.assertRaises(ValueError):
            add_vector_surveillance(
                campaign=self.campaign,
                counter="not_a_counter",
                start_trigger_condition_list=["StartSurveillance"],
                start_day=1)

    def test_invalid_duration_raises(self):
        counter = self._make_counter()
        with self.assertRaises(ValueError):
            add_vector_surveillance(
                campaign=self.campaign,
                counter=counter,
                start_trigger_condition_list=["StartSurveillance"],
                start_day=1,
                duration=-5)

    def test_invalid_species_raises(self):
        with self.assertRaises(ValueError):
            VectorCounter(
                species="",
                sample_size_distribution=ConstantDistribution(100),
                count_type=VectorCountType.ALLELE_FREQ,
                gender=VectorGender.VECTOR_FEMALE,
                update_period=30)

    def test_invalid_count_type_raises(self):
        with self.assertRaises(ValueError):
            VectorCounter(
                species="gambiae",
                sample_size_distribution=ConstantDistribution(100),
                count_type="INVALID",
                gender=VectorGender.VECTOR_FEMALE,
                update_period=30)

    def test_invalid_gender_raises(self):
        with self.assertRaises(ValueError):
            VectorCounter(
                species="gambiae",
                sample_size_distribution=ConstantDistribution(100),
                count_type=VectorCountType.ALLELE_FREQ,
                gender="INVALID",
                update_period=30)

    def test_invalid_update_period_raises(self):
        with self.assertRaises(ValueError):
            VectorCounter(
                species="gambiae",
                sample_size_distribution=ConstantDistribution(100),
                count_type=VectorCountType.ALLELE_FREQ,
                gender=VectorGender.VECTOR_FEMALE,
                update_period=-1)

    def test_invalid_sample_size_distribution_raises(self):
        with self.assertRaises(ValueError):
            VectorCounter(
                species="gambiae",
                sample_size_distribution="not_a_distribution",
                count_type=VectorCountType.ALLELE_FREQ,
                gender=VectorGender.VECTOR_FEMALE,
                update_period=30)

    def test_implicit_validates_vector_sampling_type(self):
        self.campaign.implicits.clear()
        counter = self._make_counter()
        VectorSurveillanceEventCoordinator(
            campaign=self.campaign,
            counter=counter,
            start_trigger_condition_list=["StartSurveillance"])
        self.assertEqual(len(self.campaign.implicits), 1)

        class MockConfig:
            class parameters:
                Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
        with self.assertRaises(ValueError) as ctx:
            self.campaign.implicits[0](MockConfig())
        self.assertIn("TRACK_ALL_VECTORS", str(ctx.exception))
        self.assertIn("VectorSurveillanceEventCoordinator", str(ctx.exception))

        MockConfig.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
        result = self.campaign.implicits[0](MockConfig())
        self.assertIsNotNone(result)

        MockConfig.parameters.Vector_Sampling_Type = "SAMPLE_IND_VECTORS"
        result = self.campaign.implicits[0](MockConfig())
        self.assertIsNotNone(result)

    def test_multiple_events(self):
        counter1 = self._make_counter(species="gambiae")
        counter2 = self._make_counter(species="funestus", update_period=14)
        add_vector_surveillance(
            campaign=self.campaign,
            counter=counter1,
            start_trigger_condition_list=["StartSurveillance"],
            start_day=1,
            coordinator_name="GambiaeSurveillance")
        add_vector_surveillance(
            campaign=self.campaign,
            counter=counter2,
            start_trigger_condition_list=["StartSurveillance"],
            start_day=1,
            coordinator_name="FunestusSurveillance")

        self.assertEqual(len(self.campaign.campaign_dict['Events']), 2)
        coord1 = self.campaign.campaign_dict['Events'][0].Event_Coordinator_Config
        coord2 = self.campaign.campaign_dict['Events'][1].Event_Coordinator_Config
        self.assertEqual(coord1.Counter.Species, "gambiae")
        self.assertEqual(coord1.Coordinator_Name, "GambiaeSurveillance")
        self.assertEqual(coord2.Counter.Species, "funestus")
        self.assertEqual(coord2.Counter.Update_Period, 14)
        self.assertEqual(coord2.Coordinator_Name, "FunestusSurveillance")


@pytest.mark.unit
class TestAddBroadcastCoordinatorEvent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_path = manifest.schema_path

    def setUp(self):
        self.campaign = api_campaign
        self.campaign.set_schema(self.schema_path)

    def test_default(self):
        add_broadcast_coordinator_event(
            campaign=self.campaign,
            broadcast_event="StartSurveillance",
            start_day=1)

        self.assertEqual(len(self.campaign.campaign_dict['Events']), 1)
        event = self.campaign.campaign_dict['Events'][0]
        self.assertEqual(event['class'], 'CampaignEvent')
        self.assertEqual(event.Start_Day, 1)
        self.assertEqual(event.Nodeset_Config['class'], 'NodeSetAll')

        coordinator = event.Event_Coordinator_Config
        self.assertEqual(coordinator['class'], 'BroadcastCoordinatorEvent')
        self.assertEqual(coordinator.Broadcast_Event, "StartSurveillance")
        self.assertEqual(coordinator.Coordinator_Name, "BroadcastCoordinatorEvent")
        self.assertEqual(coordinator.Cost_To_Consumer, 0)

    def test_with_all_options(self):
        add_broadcast_coordinator_event(
            campaign=self.campaign,
            broadcast_event="StartSurveillance",
            start_day=10,
            coordinator_name="MyBroadcast",
            cost_to_consumer=5.0,
            event_name="test_broadcast_event",
            node_ids=[1, 2, 3])

        self.assertEqual(len(self.campaign.campaign_dict['Events']), 1)
        event = self.campaign.campaign_dict['Events'][0]
        self.assertEqual(event['class'], 'CampaignEvent')
        self.assertEqual(event.Start_Day, 10)
        self.assertEqual(event.Event_Name, "test_broadcast_event")
        self.assertEqual(event.Nodeset_Config['class'], 'NodeSetNodeList')
        self.assertEqual(event.Nodeset_Config.Node_List, [1, 2, 3])

        coordinator = event.Event_Coordinator_Config
        self.assertEqual(coordinator['class'], 'BroadcastCoordinatorEvent')
        self.assertEqual(coordinator.Broadcast_Event, "StartSurveillance")
        self.assertEqual(coordinator.Coordinator_Name, "MyBroadcast")
        self.assertEqual(coordinator.Cost_To_Consumer, 5.0)

    def test_empty_event_raises(self):
        with self.assertRaises(ValueError) as context:
            add_broadcast_coordinator_event(
                campaign=self.campaign,
                broadcast_event="",
                start_day=1)
        self.assertIn("broadcast_event", str(context.exception))

    def test_none_event_raises(self):
        with self.assertRaises(ValueError) as context:
            add_broadcast_coordinator_event(
                campaign=self.campaign,
                broadcast_event=None,
                start_day=1)
        self.assertIn("broadcast_event", str(context.exception))

    def test_invalid_cost_raises(self):
        with self.assertRaises(ValueError):
            add_broadcast_coordinator_event(
                campaign=self.campaign,
                broadcast_event="StartSurveillance",
                start_day=1,
                cost_to_consumer=-1)

    def test_multiple_events(self):
        add_broadcast_coordinator_event(
            campaign=self.campaign,
            broadcast_event="StartSurveillance",
            start_day=1,
            coordinator_name="First")
        add_broadcast_coordinator_event(
            campaign=self.campaign,
            broadcast_event="StopSurveillance",
            start_day=365,
            coordinator_name="Second")

        self.assertEqual(len(self.campaign.campaign_dict['Events']), 2)
        coord1 = self.campaign.campaign_dict['Events'][0].Event_Coordinator_Config
        coord2 = self.campaign.campaign_dict['Events'][1].Event_Coordinator_Config
        self.assertEqual(coord1.Broadcast_Event, "StartSurveillance")
        self.assertEqual(coord1.Coordinator_Name, "First")
        self.assertEqual(coord2.Broadcast_Event, "StopSurveillance")
        self.assertEqual(coord2.Coordinator_Name, "Second")
        self.assertEqual(self.campaign.campaign_dict['Events'][1].Start_Day, 365)


if __name__ == '__main__':
    unittest.main()
