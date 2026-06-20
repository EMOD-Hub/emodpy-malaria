import pathlib

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from emodpy.emod_task import EMODTask as emod_task
from emodpy.reporters.common import DemographicsReport

import manifest

"""
Comprehensive example demonstrating ALL emodpy-malaria2 interventions, distributors,
and demographics options. Each intervention is paired with a BroadcastEvent that
broadcasts the intervention's class name.
"""


# ===========================================================================
# BUILD CAMPAIGN
# ===========================================================================
def build_campaign(campaign):
    import emod_api.campaign as campaign
    import emodpy_malaria.campaign.individual_intervention as ind
    import emodpy_malaria.campaign.node_intervention as node_iv
    import emodpy_malaria.campaign.common as common
    import emodpy_malaria.campaign.distributor as distribute
    import emodpy_malaria.campaign.waning_config as waning
    import emodpy_malaria.campaign.event_coordinator as ec
    from emodpy_malaria.utils.emod_enum import (
        DiagnosticType, NonAdherenceOption,
        HabitatType, ArtificialDietTarget,
        VectorCountType, VectorGender,
    )
    from emodpy_malaria.utils.distributions import (
        ConstantDistribution, UniformDistribution, ExponentialDistribution,
    )
    from emodpy_malaria.utils.targeting_config import HasIP, HasIntervention, IsPregnant

    campaign.set_schema(manifest.schema_file)

    day = 1

    # -----------------------------------------------------------------------
    # 1. OutbreakIndividual — seed infection
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.OutbreakIndividual(campaign),
            ind.BroadcastEvent(campaign, broadcast_event="OutbreakIndividual"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 2. AntimalarialDrug
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.AntimalarialDrug(campaign, drug_type="Chloroquine"),
            ind.BroadcastEvent(campaign, broadcast_event="AntimalarialDrug"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.05),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 3. AdherentDrug
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.AdherentDrug(
                campaign,
                doses=[["Sulfadoxine", "Pyrimethamine", "Amodiaquine"], ["Amodiaquine"], ["Amodiaquine"]],
                dose_interval=1,
                non_adherence_options=[NonAdherenceOption.NEXT_DOSAGE_TIME, NonAdherenceOption.STOP],
                non_adherence_distribution=[0.7, 0.3],
                adherence_config=waning.Constant(0.9),
                took_dose_event="TookDose",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="AdherentDrug"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.05),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 4. MultiPackComboDrug
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.MultiPackComboDrug(
                campaign,
                doses=[["Artemether", "Lumefantrine"], ["Artemether", "Lumefantrine"], ["Artemether"]],
                dose_interval=1,
            ),
            ind.BroadcastEvent(campaign, broadcast_event="MultiPackComboDrug"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.05),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 5. MalariaDiagnostic
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.MalariaDiagnostic(
                campaign,
                diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
                detection_threshold=40,
                measurement_sensitivity=0.1,
                positive_diagnosis="TestedPositive",
                negative_diagnosis="TestedNegative",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="MalariaDiagnostic"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 6. SimpleBednet
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.SimpleBednet(
                campaign,
                blocking_config=waning.Constant(0.9),
                killing_config=waning.Exponential(initial_effect=0.6, decay_time_constant=730),
                repelling_config=waning.Constant(0.4),
                usage_config=waning.Constant(0.8),
                insecticide_name="pyrethroid",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="SimpleBednet"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.6),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 7. UsageDependentBednet
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.UsageDependentBednet(
                campaign,
                blocking_config=waning.Constant(0.9),
                killing_config=waning.Exponential(initial_effect=0.7, decay_time_constant=365),
                repelling_config=waning.Constant(0.3),
                expiration_period_distribution=ExponentialDistribution(mean=730),
                usage_config_list=[waning.Constant(0.85)],
                insecticide_name="pyrethroid",
                received_event="ReceivedBednet",
                using_event="UsingBednet",
                discard_event="DiscardedBednet",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="UsageDependentBednet"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.5),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 8. MultiInsecticideUsageDependentBednet
    # -----------------------------------------------------------------------
    rbk1 = waning.InsecticideWaningEffect_RBK(
        campaign,
        repelling_config=waning.Constant(0.3),
        blocking_config=waning.Constant(0.8),
        killing_config=waning.Exponential(initial_effect=0.5, decay_time_constant=365),
        insecticide_name="pyrethroid",
    )
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.MultiInsecticideUsageDependentBednet(
                campaign,
                insecticides=[rbk1],
                expiration_period_distribution=ConstantDistribution(1095),
                received_event="ReceivedMultiBednet",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="MultiInsecticideUsageDependentBednet"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.3),
    )
    day += 5

    # # -----------------------------------------------------------------------
    # # 9. IRSHousingModification — skip individuals who already have IRS
    # # -----------------------------------------------------------------------
    # distribute.add_intervention_scheduled(
    #     campaign,
    #     intervention_list=[
    #         ind.IRSHousingModification(
    #             campaign,
    #             killing_config=waning.Exponential(initial_effect=0.5, decay_time_constant=180),
    #             repelling_config=waning.Constant(0.2),
    #             insecticide_name="pyrethroid",
    #         ),
    #         ind.BroadcastEvent(campaign, broadcast_event="IRSHousingModification"),
    #     ],
    #     start_day=day,
    #     target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.4),
    #     targeting_config=~HasIntervention(intervention_name="IRSHousingModification"),
    # )
    # day += 5

    # # -----------------------------------------------------------------------
    # # 10. MultiInsecticideIRSHousingModification
    # # -----------------------------------------------------------------------
    # rk1 = waning.InsecticideWaningEffect_RK(
    #     campaign,
    #     repelling_config=waning.Constant(0.2),
    #     killing_config=waning.Exponential(initial_effect=0.6, decay_time_constant=180),
    #     insecticide_name="pyrethroid",
    # )
    # distribute.add_intervention_scheduled(
    #     campaign,
    #     intervention_list=[
    #         ind.MultiInsecticideIRSHousingModification(campaign, insecticides=[rk1]),
    #         ind.BroadcastEvent(campaign, broadcast_event="MultiInsecticideIRSHousingModification"),
    #     ],
    #     start_day=day,
    #     target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.3),
    # )
    # day += 5

    # -----------------------------------------------------------------------
    # 11. ScreeningHousingModification
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.ScreeningHousingModification(
                campaign,
                killing_config=waning.Constant(0.1),
                repelling_config=waning.Constant(0.5),
                insecticide_name="pyrethroid",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="ScreeningHousingModification"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.3),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 12. SpatialRepellentHousingModification
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.SpatialRepellentHousingModification(
                campaign,
                repelling_config=waning.Exponential(initial_effect=0.4, decay_time_constant=365),
                insecticide_name="pyrethroid",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="SpatialRepellentHousingModification"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.2),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 13. SimpleIndividualRepellent
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.SimpleIndividualRepellent(
                campaign,
                repelling_config=waning.BoxExponential(initial_effect=0.5, box_duration=30, decay_time_constant=60),
                insecticide_name="pyrethroid",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="SimpleIndividualRepellent"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.2),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 14. IndoorIndividualEmanator
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.IndoorIndividualEmanator(
                campaign,
                killing_config=waning.Exponential(initial_effect=0.3, decay_time_constant=90),
                repelling_config=waning.Constant(0.2),
                insecticide_name="pyrethroid",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="IndoorIndividualEmanator"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.2),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 15. HumanHostSeekingTrap
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[ind.HumanHostSeekingTrap(campaign,
                                                    attract_config=waning.Constant(0.4),
                                                    killing_config=waning.Constant(0.6)),
                           ind.BroadcastEvent(campaign, broadcast_event="HumanHostSeekingTrap")],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.2),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 16. Ivermectin
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.Ivermectin(
                campaign,
                killing_config=waning.BoxExponential(initial_effect=0.9, box_duration=7, decay_time_constant=14),
                insecticide_name="pyrethroid",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="Ivermectin"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 17. RTSSVaccine — target pregnant women only
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.RTSSVaccine(campaign, boosted_antibody_concentration=1.0),
            ind.BroadcastEvent(campaign, broadcast_event="RTSSVaccine"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.3),
        targeting_config=IsPregnant(),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 18. BitingRisk
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.BitingRisk(campaign, risk_distribution=UniformDistribution(0.5, 1.5)),
            ind.BroadcastEvent(campaign, broadcast_event="BitingRisk"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
    )
    day += 5

    # -----------------------------------------------------------------------
    # 19. SimpleHealthSeekingBehavior
    # -----------------------------------------------------------------------
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.SimpleHealthSeekingBehavior(
                campaign,
                actual_intervention="SoughtCare",
                tendency=0.7,
                single_use=False,
            ),
            ind.BroadcastEvent(campaign, broadcast_event="SimpleHealthSeekingBehavior"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.5),
    )
    day += 5

    # NOTE: OutbreakIndividualMalariaGenetics and OutbreakIndividualMalariaVarGenes
    # require Malaria_Model = MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS,
    # which is incompatible with the standard malaria model used here.
    # They are omitted from this example but available in emodpy_malaria.campaign.individual_intervention.

    # -----------------------------------------------------------------------
    # Re-exported individual interventions (from emodpy)
    # -----------------------------------------------------------------------

    # 22. SimpleVaccine
    from emodpy_malaria.utils.emod_enum import VaccineType
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.SimpleVaccine(
                campaign,
                vaccine_type=VaccineType.AcquisitionBlocking,
                waning_config=waning.Exponential(initial_effect=0.8, decay_time_constant=365),
            ),
            ind.BroadcastEvent(campaign, broadcast_event="SimpleVaccine"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
    )
    day += 5

    # 23. ControlledVaccine
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.ControlledVaccine(
                campaign,
                vaccine_type=VaccineType.TransmissionBlocking,
                waning_config=waning.Box(constant_effect=0.7, box_duration=180),
                duration_to_wait_before_revaccination=365,
            ),
            ind.BroadcastEvent(campaign, broadcast_event="ControlledVaccine"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
    )
    day += 5

    # 24. PropertyValueChanger
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.PropertyValueChanger(campaign, target_property_key="DrugStatus", target_property_value="RecentDrug"),
            ind.BroadcastEvent(campaign, broadcast_event="PropertyValueChanger"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.05),
    )
    day += 5

    # 25. DelayedIntervention
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.DelayedIntervention(
                campaign,
                delay_period_distribution=ConstantDistribution(7),
                intervention_to_distribute_at_delay_completion=ind.BroadcastEvent(campaign, broadcast_event="DelayedAction"),
            ),
            ind.BroadcastEvent(campaign, broadcast_event="DelayedIntervention"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.05),
    )
    day += 5

    # 26. StandardDiagnostic
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            ind.StandardDiagnostic(
                campaign,
                positive_diagnosis_event="StandardTestPositive",
                negative_diagnosis_event="StandardTestNegative",
            ),
            ind.BroadcastEvent(campaign, broadcast_event="StandardDiagnostic"),
        ],
        start_day=day,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
    )
    day += 5

    # -----------------------------------------------------------------------
    # TRIGGERED distributor — demonstrate add_intervention_triggered
    # -----------------------------------------------------------------------

    # 27. Triggered: AntimalarialDrug on positive test — only if not already on drugs
    distribute.add_intervention_triggered(
        campaign,
        intervention_list=[
            ind.AntimalarialDrug(campaign, drug_type="Artesunate"),
            ind.BroadcastEvent(campaign, broadcast_event="TriggeredAntimalarialDrug")],
        triggers_list=["TestedPositive"],
        start_day=1,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=1.0),
        targeting_config=HasIP(ip_key_value="DrugStatus:None") & ~HasIntervention(intervention_name="AntimalarialDrug"),
    )

    # -----------------------------------------------------------------------
    # COMMUNITY HEALTH WORKER distributor
    # -----------------------------------------------------------------------

    # 28. CHW distributes Chloroquine when someone seeks care
    distribute.add_community_health_worker(
        campaign,
        intervention_list=[
            ind.AntimalarialDrug(campaign, drug_type="Chloroquine"),
            ind.BroadcastEvent(campaign, broadcast_event="CHW_AntimalarialDrug"),
        ],
        trigger_condition_list=["SoughtCare"],
        start_day=1,
        waiting_period=4,
        initial_amount_distribution=UniformDistribution(20, 100),
        days_between_shipments=30,
        amount_in_shipment=50,
        max_stock=200,
        max_distributed_per_day=5,
        target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=1.0)
    )

    # -----------------------------------------------------------------------
    # BROADCAST COORDINATOR EVENT distributor
    # -----------------------------------------------------------------------

    # 29. Broadcast a coordinator event to trigger surveillance
    distribute.add_broadcast_coordinator_event(
        campaign,
        broadcast_event="StartVectorSurveillance",
        start_day=day,
    )
    day += 5

    # -----------------------------------------------------------------------
    # VECTOR SURVEILLANCE distributor
    # -----------------------------------------------------------------------

    # 30. Vector surveillance
    # NOTE: any coordinator-level events that dtk_vector_surveillance.py's respond()
    # might return must be manually registered in Custom_Coordinator_Events in config.
    # They cannot be auto-detected from the script.
    counter = ec.VectorCounter(
        species="arabiensis",
        sample_size_distribution=ConstantDistribution(100),
        count_type=VectorCountType.ALLELE_FREQ,
        gender=VectorGender.VECTOR_FEMALE,
        update_period=30,
    )
    distribute.add_vector_surveillance(
        campaign,
        counter=counter,
        start_trigger_condition_list=["StartVectorSurveillance"],
        start_day=1,
        survey_completed_event="VectorSurveyDone",
        duration=365,
    )

    # ===================================================================
    # NODE-LEVEL INTERVENTIONS — each paired with BroadcastNodeEvent
    # ===================================================================

    # 31. SpaceSpraying
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.SpaceSpraying(campaign, killing_config=waning.Exponential(initial_effect=0.7, decay_time_constant=90), insecticide_name="pyrethroid"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="SpaceSpraying"),
        ],
        start_day=day,
    )
    day += 5

    # 32. IndoorSpaceSpraying
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.IndoorSpaceSpraying(campaign, killing_config=waning.Exponential(initial_effect=0.6, decay_time_constant=120), insecticide_name="pyrethroid"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="IndoorSpaceSpraying"),
        ],
        start_day=day,
    )
    day += 5

    # 33. MultiInsecticideSpaceSpraying
    ik1 = waning.InsecticideWaningEffect_K(
        campaign,
        killing_config=waning.Exponential(initial_effect=0.5, decay_time_constant=90),
        insecticide_name="pyrethroid",
    )
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.MultiInsecticideSpaceSpraying(campaign, insecticides=[ik1]),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="MultiInsecticideSpaceSpraying"),
        ],
        start_day=day,
    )
    day += 5

    # 34. MultiInsecticideIndoorSpaceSpraying
    ik2 = waning.InsecticideWaningEffect_K(
        campaign,
        killing_config=waning.Exponential(initial_effect=0.6, decay_time_constant=120),
        insecticide_name="pyrethroid",
    )
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.MultiInsecticideIndoorSpaceSpraying(campaign, insecticides=[ik2]),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="MultiInsecticideIndoorSpaceSpraying"),
        ],
        start_day=day,
    )
    day += 5

    # 35. Larvicides
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.Larvicides(campaign, killing_config=waning.Constant(0.7), habitat_target=HabitatType.ALL_HABITATS, insecticide_name="pyrethroid"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="Larvicides"),
        ],
        start_day=day,
    )
    day += 5

    # 36. LarvalMicrosporidiaIntervention
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.LarvalMicrosporidiaIntervention(
                campaign, strain_name="Strain_A", habitat_coverage=0.5,
                infectivity_config=waning.Constant(0.4)),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="LarvalMicrosporidiaIntervention"),
        ],
        start_day=day,
    )
    day += 5

    # 37. InputEIR (monthly)
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.InputEIR(campaign, monthly_eir=[5, 10, 20, 30, 25, 15, 10, 8, 12, 18, 10, 5]),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="InputEIR"),
        ],
        start_day=day,
    )
    day += 5

    # 38. MalariaChallenge
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.MalariaChallenge(campaign, infectious_bite_count=3, coverage=0.5),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="MalariaChallenge"),
        ],
        start_day=day,
    )
    day += 5

    # 39. MosquitoRelease
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.MosquitoRelease(
                campaign,
                released_species="arabiensis",
                released_genome=[["X", "Y"], ["a0", "a0"]],
                released_number=10000),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="MosquitoRelease"),
        ],
        start_day=day,
    )
    day += 5

    # 40. ScaleLarvalHabitat
    spec = node_iv.LarvalHabitatMultiplierSpec(campaign, habitat=HabitatType.TEMPORARY_RAINFALL, factor=0.5)
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.ScaleLarvalHabitat(campaign, larval_habitat_multiplier=[spec]),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="ScaleLarvalHabitat"),
        ],
        start_day=day,
    )
    day += 5

    # 41. OutdoorRestKill
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.OutdoorRestKill(campaign, killing_config=waning.Constant(0.3), insecticide_name="pyrethroid"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="OutdoorRestKill"),
        ],
        start_day=day,
    )
    day += 5

    # 42. OutdoorNodeEmanator
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.OutdoorNodeEmanator(campaign, repelling_config=waning.Constant(0.2), killing_config=waning.Constant(0.3), insecticide_name="pyrethroid"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="OutdoorNodeEmanator"),
        ],
        start_day=day,
    )
    day += 5

    # 43. SugarTrap
    distribute.add_intervention_scheduled(campaign,
                                          intervention_list=[node_iv.SugarTrap(campaign,
                                                                               killing_config=waning.Exponential(initial_effect=0.5,
                                                                                                                 decay_time_constant=60),
                                                                               expiration_period_distribution=ConstantDistribution(365),
                                                                               insecticide_name="pyrethroid"),
                                                             node_iv.BroadcastNodeEvent(campaign, broadcast_event="SugarTrap")],
                                          start_day=day)
    day += 5

    # NOTE: OvipositionTrap requires the individual-mosquito model (Vector_Sampling_Type
    # = TRACK_ALL_VECTORS), not the default cohort model. It is omitted from this example.

    # 44. SpatialRepellent (node-level)
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.SpatialRepellent(campaign, repelling_config=waning.Constant(0.3), insecticide_name="pyrethroid"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="SpatialRepellent"),
        ],
        start_day=day,
    )
    day += 5

    # 46. AnimalFeedKill
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.AnimalFeedKill(campaign, killing_config=waning.Constant(0.4), insecticide_name="pyrethroid"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="AnimalFeedKill"),
        ],
        start_day=day,
    )
    day += 5

    # 47. ArtificialDiet
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.ArtificialDiet(
                campaign,
                artificial_diet_target=ArtificialDietTarget.AD_WITHIN_VILLAGE,
                attraction_config=waning.Constant(0.3)),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="ArtificialDiet"),
        ],
        start_day=day,
    )
    day += 5

    # 48. Re-exported node interventions: Outbreak
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.Outbreak(campaign, number_cases_per_node=5),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="Outbreak"),
        ],
        start_day=day,
    )
    day += 5

    # 49. NodePropertyValueChanger
    distribute.add_intervention_scheduled(
        campaign,
        intervention_list=[
            node_iv.NodePropertyValueChanger(campaign, target_np_key_value="NodeQuality:Good"),
            node_iv.BroadcastNodeEvent(campaign, broadcast_event="NodePropertyValueChanger"),
        ],
        start_day=day,
    )

    return campaign


# ===========================================================================
# BUILD CONFIG
# ===========================================================================
def build_config(config):
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["arabiensis", "funestus"])
    malaria_config.add_genes_and_alleles(config, manifest, species="arabiensis",
                                         alleles=[("a0", 0.8),("a1", 0.1),("a2", 0.1)])
    malaria_config.add_insecticide_resistance(config, manifest, insecticide_name="pyrethroid",
                                              species="arabiensis", allele_combo=[["a1", "a1"]],
                                              blocking=1, repelling=0.5, killing=0.9)
    malaria_config.add_blood_meal_mortality(config, manifest, species="arabiensis", allele_combo=[["a0", "a2"]],
                                            default_probability_of_death=0.00001,
                                            probability_of_death_for_allele_combo=0.0001)
    vector_config.add_microsporidia(config, manifest, species_name="arabiensis", strain_name="Strain_A")
    vector_config.set_species_param(config, "arabiensis", "Vector_Sugar_Feeding_Frequency",
                                    "VECTOR_SUGAR_FEEDING_EVERY_DAY")
    config.parameters.Simulation_Duration = 365
    config.parameters.Vector_Sampling_Type = "SAMPLE_IND_VECTORS"
    # we need to add the coordinator-level events that can be generated by the respond() function in
    # dtk_vector_surveillance.py manually, since they cannot be auto-detected from the script due to
    # potential to be dynamically generated based on survey results.
    # ex: (f"Release_{vector_species}") you'd need to add all the potential events that can be generated.
    config.parameters.Custom_Coordinator_Events = ["VectorCoordinatorResponderEvent"]
    return config


# ===========================================================================
# BUILD DEMOGRAPHICS — all malaria demographics options
# ===========================================================================
def build_demographics():
    from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
    from emodpy_malaria.utils.distributions import UniformDistribution, ExponentialDistribution
    from emodpy_malaria.utils.emod_enum import InnateImmuneVariationType

    # from_template_node — single-node factory
    demographics = MalariaDemographics.from_template_node(pop=1000)

    # add_individual_property
    demographics.add_individual_property(
        property="DrugStatus", values=["None", "RecentDrug"], initial_distribution=[1, 0])

    # add_node_property
    demographics.add_node_property(
        property="NodeQuality", values=["Good", "Bad"], initial_distribution=[0.5, 0.5])

    # set_age_distribution
    demographics.set_age_distribution(UniformDistribution(0, 50 * 365))

    # set_birth_rate — INDIVIDUAL_PREGNANCIES assigns pregnancies individually with 40-week gestation
    demographics.set_birth_rate(rate=4, birth_rate_dependence="INDIVIDUAL_PREGNANCIES")

    # set_risk_distribution — malaria-specific heterogeneous biting
    demographics.set_risk_distribution(ExponentialDistribution(mean=1.0))

    # set_innate_immune_distribution — malaria-specific innate immunity
    demographics.set_innate_immune_distribution(
        distribution=UniformDistribution(0, 1),
        innate_immune_variation_type=InnateImmuneVariationType.CYTOKINE_KILLING,
    )

    return demographics


# ===========================================================================
# ADD REPORTS
# ===========================================================================
def add_reports(reporters):
    from emodpy_malaria.reporters.reporters import (
        ReportEventRecorder, ReportNodeEventRecorder, ReportCoordinatorEventRecorder,
    )
    # "IRSHousingModification", "MultiInsecticideIRSHousingModification" NOT USED
    individual_events = [ "Births",
        "OutbreakIndividual", "AntimalarialDrug", "AdherentDrug", "MultiPackComboDrug",
        "MalariaDiagnostic", "SimpleBednet", "UsageDependentBednet",
        "MultiInsecticideUsageDependentBednet", "ScreeningHousingModification",
        "SpatialRepellentHousingModification", "SimpleIndividualRepellent",
        "IndoorIndividualEmanator", "HumanHostSeekingTrap", "Ivermectin",
        "RTSSVaccine", "BitingRisk", "SimpleHealthSeekingBehavior",
        "SimpleVaccine", "ControlledVaccine", "PropertyValueChanger",
        "DelayedIntervention", "StandardDiagnostic",
        "TriggeredAntimalarialDrug", "CHW_AntimalarialDrug",
        "TestedPositive", "TestedNegative", "StandardTestPositive", "StandardTestNegative",
        "TookDose", "ReceivedBednet", "UsingBednet", "DiscardedBednet",
        "ReceivedMultiBednet", "SoughtCare", "DelayedAction",
    ]
    reporters.add(ReportEventRecorder(reporters, event_list=individual_events))

    node_events = [
        "SpaceSpraying", "IndoorSpaceSpraying",
        "MultiInsecticideSpaceSpraying", "MultiInsecticideIndoorSpaceSpraying",
        "Larvicides", "LarvalMicrosporidiaIntervention",
        "InputEIR", "MalariaChallenge", "MosquitoRelease",
        "ScaleLarvalHabitat", "OutdoorRestKill", "OutdoorNodeEmanator",
        "SugarTrap", "SpatialRepellent",
        "AnimalFeedKill", "ArtificialDiet",
        "Outbreak", "NodePropertyValueChanger",
    ]
    reporters.add(ReportNodeEventRecorder(reporters, event_list=node_events))

    coordinator_events = ["StartVectorSurveillance", "VectorSurveyDone"]
    reporters.add(ReportCoordinatorEventRecorder(reporters, event_list=coordinator_events))

    reporters.add(DemographicsReport(reporters))

    return reporters


# ===========================================================================
# RUN SIMULATION
# ===========================================================================
def run_sim():
    platform = Platform(manifest.plat_name, job_directory=manifest.job_dir, docker_image=manifest.plat_image)

    task = emod_task.from_defaults(
        eradication_path=manifest.eradication_path,
        schema_path=manifest.schema_file,
        config_builder=build_config,
        campaign_builder=build_campaign,
        demographics_builder=build_demographics,
        report_builder=add_reports,
        embedded_python_scripts_path=str(pathlib.Path(__file__).parent / "dtk_vector_surveillance.py")
    )

    experiment = Experiment.from_task(task=task, name="most_interventions_example")
    experiment.run(wait_until_done=True, platform=platform)

    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
        exit()

    print(f"Experiment {experiment.id} succeeded.")

    with open("experiment_id", "w") as fd:
        fd.write(experiment.id)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_sim()
