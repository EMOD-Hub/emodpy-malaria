from emodpy.campaign.individual_intervention import BroadcastEvent as BroadcastEvent
from emodpy.campaign.individual_intervention import BroadcastEventToOtherNodes as BroadcastEventToOtherNodes
from emodpy.campaign.individual_intervention import ControlledVaccine as ControlledVaccine
from emodpy.campaign.individual_intervention import DelayedIntervention as DelayedIntervention
from emodpy.campaign.individual_intervention import IndividualImmunityChanger as IndividualImmunityChanger
from emodpy.campaign.individual_intervention import IndividualNonDiseaseDeathRateModifier as IndividualNonDiseaseDeathRateModifier
from emodpy.campaign.individual_intervention import MigrateIndividuals as MigrateIndividuals
from emodpy.campaign.individual_intervention import MultiEffectBoosterVaccine as MultiEffectBoosterVaccine
from emodpy.campaign.individual_intervention import MultiEffectVaccine as MultiEffectVaccine
from emodpy.campaign.individual_intervention import MultiInterventionDistributor as MultiInterventionDistributor
from emodpy.campaign.individual_intervention import OutbreakIndividual as OutbreakIndividual
from emodpy.campaign.individual_intervention import PropertyValueChanger as PropertyValueChanger
from emodpy.campaign.individual_intervention import SimpleBoosterVaccine as SimpleBoosterVaccine
from emodpy.campaign.individual_intervention import SimpleVaccine as SimpleVaccine
from emodpy.campaign.individual_intervention import StandardDiagnostic as StandardDiagnostic
from emodpy.campaign.individual_intervention import IndividualIntervention
from emodpy.campaign.individual_intervention import IVCalendar as IVCalendar
from emodpy.campaign.individual_intervention import FemaleContraceptive as FemaleContraceptive
from emodpy.utils import validate_value_range
from emodpy.campaign.utils import set_event
from emodpy_malaria.campaign.common import CommonInterventionParameters
from emodpy_malaria.campaign.waning_config import AbstractWaningConfig, Constant, InsecticideWaningEffect
from emodpy_malaria.utils.emod_enum import NonAdherenceOption, DiagnosticType, NucleotideSequenceOrigin, EventOrConfig
from emodpy_malaria.utils.config_utils import validate_insecticide_name, validate_malaria_model, validate_genome_locations_length
from emod_api import campaign as api_campaign
from emodpy_malaria.utils.distributions import BaseDistribution

from typing import Union
from functools import partial


class AntimalarialDrug(IndividualIntervention):
    """
    The **AntimalarialDrug** intervention class distributes an antimalarial drug to an individual.
    The drug's pharmacokinetic and pharmacodynamic parameters are configured in the config file
    via **Malaria_Drug_Params**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        drug_type (str, required):
            The name of the antimalarial drug to distribute. Must match a drug name configured
            in the simulation's Malaria_Drug_Params.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 drug_type: str,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AntimalarialDrug', common_intervention_parameters)
        self._intervention.Drug_Type = drug_type


class AdherentDrug(IndividualIntervention):
    """
    The **AdherentDrug** intervention class extends antimalarial drug distribution of the **MultiPackComboDrug**
    intervention with adherence modeling. It allows configuring dose schedules, adherence patterns,
    and non-adherence behaviors, simulating patients who may not take every dose as prescribed.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        doses (list[list[str]], required):
            A two-dimensional array of drug names defining the drug regimen. Each inner list represents
            the drugs taken in a single dose. All drug names must match those defined in the
            simulation's Malaria_Drug_Params.

            Example -- a standard 3-day AL (Artemether-Lumefantrine) regimen with 6 doses::

                doses = [
                    ["Artemether", "Lumefantrine"],  # dose 1 (day 0)
                    ["Artemether", "Lumefantrine"],  # dose 2 (day 0 + 8h)
                    ["Artemether", "Lumefantrine"],  # dose 3 (day 1)
                    ["Artemether", "Lumefantrine"],  # dose 4 (day 1 + 8h)
                    ["Artemether"],  # dose 5 (day 2)
                    ["Artemether"],  # dose 6 (day 2 + 8h)
                ]

            Example -- a single-dose SP (Sulfadoxine-Pyrimethamine) for IPTp::

                doses = [["Sulfadoxine", "Pyrimethamine"]]

        adherence_config (AbstractWaningConfig, required):
            Configuration for the probability of taking a dose. Use a waning effect class
            to specify how this probability changes over time.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

            Example -- 80% adherence that stays constant throughout the regimen::

                from emodpy_malaria.campaign.waning_config import Constant
                adherence_config = Constant(campaign, initial_effect=0.8)

            Example -- adherence that decays from 90% to 50% over the course of a 3-day regimen::

                from emodpy_malaria.campaign.waning_config import BoxExponential
                adherence_config = BoxExponential(campaign, initial_effect=0.9,
                                                  box_duration=0, decay_rate=0.2)

        non_adherence_options (list[NonAdherenceOption], required):
            List of options for what happens when a dose is missed. Each entry defines a
            possible non-adherence behavior; the corresponding probability of each behavior
            is set in **non_adherence_distribution**. Use the
            [NonAdherenceOption](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) enum values:

            * ``NonAdherenceOption.NEXT_UPDATE`` -- The person does not take the dose during
              this update but will reconsider at the next update (and may still not take it).
              If the person is infected, the time to the next update depends on
              Infection_Updates_Per_Timestep, which is usually 8 updates per day which the
              same as timestep for malaria_sim.
            * ``NonAdherenceOption.NEXT_DOSAGE_TIME`` -- The person missed a dose and waits
              until the next scheduled dosage time to take the pill, staying on the prescribed
              dosage schedule.
            * ``NonAdherenceOption.LOST_TAKE_NEXT`` -- The person lost the dose and takes the
              next dose in the pill pack, reducing the total number of pills taken.
            * ``NonAdherenceOption.STOP`` -- The person stops taking the pills entirely (or has
              lost the pill pack). Pills taken prior to stopping still have an effect, but no
              remaining pills will be taken.

            Example -- most people who miss a dose wait for the next scheduled time, but
            some stop entirely::

                non_adherence_options = [
                    NonAdherenceOption.NEXT_DOSAGE_TIME,
                    NonAdherenceOption.STOP,
                ]

        non_adherence_distribution (list[float], required):
            Probability distribution across non-adherence options. Must sum to 1.0
            and have the same length as **non_adherence_options**. Each value is the probability
            of the corresponding non-adherence behavior when a dose is missed.

            Example -- matching the options above, 90% wait for next dose time, 10% stop::

                non_adherence_distribution = [0.9, 0.1]

        dose_interval (float, optional):
            The number of days between **doses** which are defined in the **doses** parameter.
            Minimum value: 0
            Maximum value: 100000
            Default value: 1

            Example -- twice-daily dosing for an AL regimen::

                dose_interval = 0.5

        max_dose_consideration_duration (float, optional):
            Maximum number of days the person will consider (attempt) taking remaining **doses**. After this
            duration, any remaining **doses** in the regimen are abandoned.
            Minimum value: 0.0416667
            Maximum value: 3.40282e+38
            Default value: 3.40282e+38

            Example -- give up on the regimen after 7 days regardless of adherence::

                max_dose_consideration_duration = 7

        took_dose_event (str, optional):
            An individual-level event to broadcast each time a dose is successfully taken. Useful for tracking
            adherence or triggering follow-up actions.
            Default value: None

            Example -- broadcast an event to count **doses** taken::

                took_dose_event = "TookALDose"

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters:
            cost, intervention_name, new_property_value, disqualifying_properties,
            dont_allow_duplicates.
            Default value: None

    Example:
        A 3-day AL regimen with once-every-two days, 80% constant adherence, and mixed
        non-adherence behaviors::

            from emodpy_malaria.campaign.individual_intervention import AdherentDrug
            from emodpy_malaria.campaign.waning_config import Constant
            from emodpy_malaria.utils.emod_enum import NonAdherenceOption

            drug = AdherentDrug(
                campaign=campaign,
                doses=[
                    ["Artemether", "Lumefantrine"],
                    ["Artemether", "Lumefantrine"],
                    ["Artemether", "Lumefantrine"],
                    ["Artemether", "Lumefantrine"],
                    ["Artemether", "Lumefantrine"],
                    ["Artemether", "Lumefantrine"],
                ],
                adherence_config=Constant(campaign, initial_effect=0.8),
                non_adherence_options=[
                    NonAdherenceOption.NEXT_DOSAGE_TIME,
                    NonAdherenceOption.LOST_TAKE_NEXT,
                    NonAdherenceOption.STOP,
                ],
                non_adherence_distribution=[0.6, 0.3, 0.1],
                dose_interval=2,
                max_dose_consideration_duration=7,
                took_dose_event="TookALDose",
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 doses: list[list[str]],
                 adherence_config: AbstractWaningConfig,
                 non_adherence_options: list[NonAdherenceOption],
                 non_adherence_distribution: list[float],
                 dose_interval: float = 1,
                 max_dose_consideration_duration: float = 3.40282e+38,
                 took_dose_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):

        super().__init__(campaign, 'AdherentDrug', common_intervention_parameters)

        if len(doses) * dose_interval > max_dose_consideration_duration:
            raise ValueError("'max_dose_consideration_duration' is shorter than the total duration of the dosing regimen "
                             "defined by 'doses' and 'dose_interval' parameters. This means not all doses will be taken "
                             "even if taken successfully every time. Please adjust these parameters so "
                             "that all doses can be considered within the 'max_dose_consideration_duration'.")

        self._intervention.Doses = doses
        self._intervention.Dose_Interval = validate_value_range(dose_interval, 'dose_interval', 0, 100000, float)
        self._intervention.Max_Dose_Consideration_Duration = validate_value_range(
            max_dose_consideration_duration, 'max_dose_consideration_duration', 0.0416667, 3.40282e+38, float)

        self._intervention.Adherence_Config = adherence_config.to_schema_dict(campaign)

        for i, opt in enumerate(non_adherence_options):
            if not isinstance(opt, NonAdherenceOption):
                raise ValueError(
                    f"Each entry in 'non_adherence_options' must be a NonAdherenceOption enum value, got {opt!r}. "
                    f"Valid options: {list(NonAdherenceOption)}")
        self._intervention.Non_Adherence_Options = list(non_adherence_options)

        if len(non_adherence_distribution) != len(non_adherence_options):
            raise ValueError(
                f"'non_adherence_distribution' (length {len(non_adherence_distribution)}) must have the same "
                f"'length as non_adherence_options' (length {len(non_adherence_options)}).")
        self._intervention.Non_Adherence_Distribution = non_adherence_distribution

        if took_dose_event is not None:
            self._intervention.Took_Dose_Event = set_event(took_dose_event, 'took_dose_event', campaign, False)


class MultiPackComboDrug(IndividualIntervention):
    """
    The **MultiPackComboDrug** intervention class distributes a combination drug regimen with
    multiple doses. Similar to AdherentDrug but without adherence modeling.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        doses (list[list[str]], required):
            A two-dimensional array of drug names defining the drug regimen. Each inner list represents
            the drugs taken in a single dose. All drug names must match those defined in the
            simulation's Malaria_Drug_Params.

            Example -- a standard 3-day AL (Artemether-Lumefantrine) regimen with 6 doses::

                doses = [
                    ["Artemether", "Lumefantrine"],  # dose 1 (day 0)
                    ["Artemether", "Lumefantrine"],  # dose 2 (day 0 + 8h)
                    ["Artemether", "Lumefantrine"],  # dose 3 (day 1)
                    ["Artemether", "Lumefantrine"],  # dose 4 (day 1 + 8h)
                    ["Artemether"],  # dose 5 (day 2)
                    ["Artemether"],  # dose 6 (day 2 + 8h)
                ]

            Example -- a single-dose SP (Sulfadoxine-Pyrimethamine) for IPTp::

                doses = [["Sulfadoxine", "Pyrimethamine"]]

        dose_interval (float, optional):
            The number of days between **doses** which are defined in the **doses** parameter.
            Minimum value: 0
            Maximum value: 100000
            Default value: 1

            Example -- twice-daily dosing for an AL regimen::

                dose_interval = 0.5

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 doses: list[list[str]],
                 dose_interval: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiPackComboDrug', common_intervention_parameters)

        self._intervention.Doses = doses
        self._intervention.Dose_Interval = validate_value_range(dose_interval, 'dose_interval', 0, 100000, float)


class MalariaDiagnostic(IndividualIntervention):
    """
    The **MalariaDiagnostic** intervention class tests an individual for malaria using a specified
    diagnostic type and broadcasts events based on the result.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        diagnostic_type (DiagnosticType, required):
            The type of malaria diagnostic to use. The diagnostic type determines how the
            test measurement is made and what units **detection_threshold** and
            **measurement_sensitivity** use. Use the
            [DiagnosticType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) enum values:

            * ``DiagnosticType.BLOOD_SMEAR_PARASITES`` -- A sample of blood is viewed under
              a microscope and the number of parasites per microliter of blood is counted.
              This diagnostic includes Poisson sampling noise because real-world smear tests
              may not perfectly measure parasite levels. **detection_threshold** is in
              parasites per microliter. Uses the **measurement_sensitivity** parameter; a
              positive diagnosis is made if measurement > detection_threshold, where::

                  measurement = (1 / measurement_sensitivity) * Poisson(measurement_sensitivity * true_parasite_density)

            * ``DiagnosticType.BLOOD_SMEAR_GAMETOCYTES`` -- A sample of blood is viewed
              under a microscope and the number of gametocytes per microliter of blood is
              counted. Same Poisson sampling noise as BLOOD_SMEAR_PARASITES.
              **detection_threshold** is in gametocytes per microliter. Uses
              **measurement_sensitivity**; a positive diagnosis is made if
              measurement > detection_threshold, where::

                  measurement = (1 / measurement_sensitivity) * Poisson(measurement_sensitivity * true_gametocyte_density)

            * ``DiagnosticType.PCR_PARASITES`` -- Models a quantitative nucleic acid
              sequence-based amplification (QT-NASBA) measurement of parasite density using
              a random Gaussian distribution. **detection_threshold** is in parasites per
              microliter. Based on `Improving statistical inference on pathogen densities
              <http://dx.doi.org/10.1186/s12859-014-0402-2>`_.
            * ``DiagnosticType.PCR_GAMETOCYTES`` -- Models a QT-NASBA measurement of
              gametocyte density using a random Gaussian distribution.
              **detection_threshold** is in gametocytes per microliter. Based on the same
              paper as PCR_PARASITES.
            * ``DiagnosticType.PF_HRP2`` -- Measures picograms of Plasmodium falciparum
              histidine-rich protein 2 (HRP2) per microliter of blood.
              **detection_threshold** is in picograms of HRP2 per microliter. Modeled with
              boost and decay parameters based on `Modelling the dynamics of PfHRP2
              <https://doi.org/10.1186/1475-2875-11-74>`_.
            * ``DiagnosticType.TRUE_PARASITE_DENSITY`` -- Returns the true modeled parasite
              density with no measurement noise. **detection_threshold** is in parasites per
              microliter. Useful for model validation.
            * ``DiagnosticType.FEVER`` -- Tests whether the individual currently has a
              fever. **detection_threshold** is in degrees Celsius above normal body
              temperature (37 C). For example, a threshold of 2 triggers a positive diagnosis
              for body temperatures above 39 C. Uses a cytokine model based on
              [Innate immunity to malaria](https://doi.org/10.1038/nri1311).
            * ``DiagnosticType.FEVER_AND_SMEAR`` -- Combines fever detection with a blood
              smear test; both conditions must be positive for a positive diagnosis.

        detection_threshold (float, required):
            The diagnostic detection threshold whose units depend on the
            **diagnostic_type** setting. The measurement must be greater than this
            threshold to trigger a positive diagnosis, therefore the default of 0 generates a positive
            diagnosis at any positive value. Use the following units based on the diagnostic type:

            * ``BLOOD_SMEAR_PARASITES`` -- parasites per microliter of blood.
            * ``BLOOD_SMEAR_GAMETOCYTES`` -- gametocytes per microliter of blood.
            * ``PCR_PARASITES`` -- parasites per microliter of blood.
            * ``PCR_GAMETOCYTES`` -- gametocytes per microliter of blood.
            * ``PF_HRP2`` -- picograms of HRP2 per microliter of blood.
            * ``TRUE_PARASITE_DENSITY`` -- parasites per microliter of blood.
            * ``FEVER`` / ``FEVER_AND_SMEAR`` -- degrees Celsius above normal body
              temperature (37 C).

            Minimum value: 0
            Maximum value: 1000000

        measurement_sensitivity (float, required):
            The volume of blood tested in microliters, used to simulate Poisson sampling
            noise in blood smear diagnostics. Only applies when **diagnostic_type** is
            ``DiagnosticType.BLOOD_SMEAR_PARASITES`` or ``DiagnosticType.BLOOD_SMEAR_GAMETOCYTES``.

            The diagnostic measurement is calculated as::

                measurement = (1 / measurement_sensitivity) * Poisson(measurement_sensitivity * true_density)

            where ``true_density`` is the true parasite or gametocyte density in parasites
            per microliter. A smaller value means less blood is sampled, producing noisier
            measurements with more Poisson variability. A larger value means more blood is
            sampled, producing measurements closer to the true density. The resulting
            measurement is compared against **detection_threshold** to determine the test
            result.

            Minimum value: 0
            Maximum value: 1000000
            Default value: 0.1

        treatment_fraction (float, optional):
            Fraction of positive diagnoses that receive the action specified in
            **positive_diagnosis**. This allows modeling imperfect treatment
            coverage after diagnosis. Negative diagnoses are unaffected regardless of this parameter, all are received.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        positive_diagnosis (Union[str, IndividualIntervention], required):
            The action to take on positive diagnosis. If a string, it is broadcast as an
            individual-level event after **days_to_diagnosis**. If an ``IndividualIntervention``,
            it is distributed to the individual on positive diagnosis after **days_to_diagnosis**.
            Both positive_diagnosis and **negative_diagnosis** must be the same type
            (both strings or both ``IndividualIntervention`` instances).

        negative_diagnosis (Union[str, IndividualIntervention], optional):
            The action to take on negative diagnosis. If a string, it is broadcast as an
            individual-level event immediately. If an ``IndividualIntervention``, it is distributed to the
            individual on negative diagnosis immediately.
            Must be the same type as **positive_diagnosis** (both strings or both
            ``IndividualIntervention`` instances).
            Default value: None

        days_to_diagnosis (float, optional):
            Number of days between test administration and diagnosis result (event broadcast or
            intervention distribution). This allows modeling delays in receiving test results or
            seeking treatment after diagnosis.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 0

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None

    Example:
        Test for malaria using blood smear and broadcast an event on positive result::

            from emodpy_malaria.campaign.individual_intervention import MalariaDiagnostic
            from emodpy_malaria.utils.emod_enum import DiagnosticType

            diagnostic = MalariaDiagnostic(
                campaign=campaign,
                diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
                detection_threshold=40,
                measurement_sensitivity=0.1,
                positive_diagnosis="TestedPositive",
                negative_diagnosis="TestedNegative",
            )

    Example:
        Use an RDT and distribute a drug on positive diagnosis::

            from emodpy_malaria.campaign.individual_intervention import MalariaDiagnostic, AntimalarialDrug
            from emodpy_malaria.utils.emod_enum import DiagnosticType

            diagnostic = MalariaDiagnostic(
                campaign=campaign,
                diagnostic_type=DiagnosticType.PF_HRP2,
                detection_threshold=20,
                measurement_sensitivity=0.1,
                positive_diagnosis=AntimalarialDrug(campaign, drug_type="Chloroquine"),
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 diagnostic_type: DiagnosticType,
                 positive_diagnosis: Union[str, IndividualIntervention],
                 detection_threshold: float = 0,
                 measurement_sensitivity: float = 0.1,
                 treatment_fraction: float = 1,
                 negative_diagnosis: Union[str, IndividualIntervention] = None,
                 days_to_diagnosis: float = 0,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MalariaDiagnostic', common_intervention_parameters)

        if not isinstance(diagnostic_type, DiagnosticType):
            raise ValueError(
                f"diagnostic_type must be a DiagnosticType enum value, got {diagnostic_type!r}. "
                f"Valid options: {list(DiagnosticType)}")
        self._intervention.Diagnostic_Type = diagnostic_type

        self._intervention.Detection_Threshold = validate_value_range(
            detection_threshold, 'detection_threshold', 0, 1000000, float)
        self._intervention.Measurement_Sensitivity = validate_value_range(
            measurement_sensitivity, 'measurement_sensitivity', 0, 1000000, float)
        self._intervention.Treatment_Fraction = validate_value_range(
            treatment_fraction, 'treatment_fraction', 0, 1, float)
        self._intervention.Days_To_Diagnosis = validate_value_range(
            days_to_diagnosis, 'days_to_diagnosis', 0, 3.40282e+38, float)

        if isinstance(positive_diagnosis, str):
            self._intervention.Event_Or_Config = EventOrConfig.Event
            self._intervention.Positive_Diagnosis_Event = set_event(
                positive_diagnosis, 'positive_diagnosis', campaign, False)
            if negative_diagnosis is not None:
                if not isinstance(negative_diagnosis, str):
                    raise ValueError(
                        "'negative_diagnosis' must be a string (event name) when "
                        "'positive_diagnosis' is a string.")
                self._intervention.Negative_Diagnosis_Event = set_event(
                    negative_diagnosis, 'negative_diagnosis', campaign, False)
        elif isinstance(positive_diagnosis, IndividualIntervention):
            self._intervention.Event_Or_Config = EventOrConfig.Config
            self._intervention.Positive_Diagnosis_Config = positive_diagnosis.to_schema_dict()
            if negative_diagnosis is not None:
                if not isinstance(negative_diagnosis, IndividualIntervention):
                    raise ValueError(
                        "'negative_diagnosis' must be an IndividualIntervention when "
                        "'positive_diagnosis' is an IndividualIntervention.")
                self._intervention.Negative_Diagnosis_Config = negative_diagnosis.to_schema_dict()
        else:
            raise ValueError(
                f"'positive_diagnosis' must be a string (event name) or an IndividualIntervention, "
                f"got {type(positive_diagnosis).__name__}.")


class SimpleBednet(IndividualIntervention):
    """
    The **SimpleBednet** intervention class implements insecticide-treated nets (ITN) in the
    simulation. ITNs are a key component of modern malaria control efforts, and have recently
    been scaled up towards universal coverage in sub-Saharan Africa. Modern bednets are made of
    a polyethylene or polyester mesh, which is impregnated with a slowly releasing pyrethroid
    insecticide. When mosquitoes that are seeking a blood meal indoors encounter a net, the
    feeding attempt may be repelled due to the presence of insecticides or blocked as long as
    the net retains its physical integrity and has been correctly installed. Blocked feeding
    attempts also carry the possibility of killing the mosquito. Net ownership is configured
    through the demographic coverage, and the repelling, blocking, and killing rates of
    mosquitoes are time-dependent. All the efficacies are also affected by the usage_config
    parameter -- the usage effect is multiplied by the repelling, blocking, and killing effects
    to determine the final efficacy of the net on any given day.

    **SimpleBednet** can model the nightly bednet usage of net owners by reducing the daily efficacy.
    To model individuals using nets intermittently, see
    [UsageDependentBednet](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/). To include
    multiple insecticides, see
    [MultiInsecticideUsageDependentBednet](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/).

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target specific species or other subgroups via insecticide configuration.
    * Time-based expiration: No, but expires if the WaningEffect expires.
    * Purge existing: Yes. A new bednet replaces any other bednet intervention for this same user.
    * Vector killing contributes to: Indoor Die Before Feeding
    * Vector effects: Repelling, blocking, killing
    * Vector sexes affected: Indoor meal-seeking females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the bednet's mosquito repelling effect. This is the first effect applied
            to meal-seeking mosquitoes that encounter the net. Repelled vectors do not enter the netted space —
            they survive and do not attempt to feed again until the following day and are not affected by the
            blocking or killing effects.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        blocking_config (AbstractWaningConfig, required):
            Waning effect configuration for the bednet's ability to block meal-seeking mosquito. The blocking_config
            probabilities are applied to the subset of meal-seeking mosquitoes that have not been repelled.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            Waning effect configuration for the bednet's insecticidal killing effect. For meal-seeking vector to be
            affected, it must be successfully blocked first, mimicking mosquito landing on the bednet,
            so killing_config probabilities are applied to the subset of mosquitoes that are blocked.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        usage_config (AbstractWaningConfig, optional):
            Waning effect configuration for nightly bednet usage over time. The usage effect is multiplied with the
            repelling, blocking, and killing effects to determine the final efficacy of the net on any given night.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).
            Default value: Constant usage with initial effect of 1 (full usage)

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 blocking_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 usage_config: AbstractWaningConfig = None,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SimpleBednet', common_intervention_parameters)

        self._intervention.Blocking_Config = blocking_config.to_schema_dict(campaign)
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)

        if usage_config is not None:
            self._intervention.Usage_Config = usage_config.to_schema_dict(campaign)
        else:
            self._intervention.Usage_Config = Constant(constant_effect=1).to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class UsageDependentBednet(IndividualIntervention):
    """
    The **UsageDependentBednet** intervention class is similar to
    [SimpleBednet](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/), as it distributes
    insecticide-treated nets to individuals in the simulation. However, bednet ownership and
    nightly bednet usage are distinct in this intervention. As in **SimpleBednet**, net ownership
    is configured through the demographic coverage, and the repelling, blocking, and killing
    rates of mosquitoes are time-dependent. Nightly use of bednets is age-dependent and can
    vary seasonally. Once a net has been distributed to someone, the nightly net usage is
    determined by the product of the seasonal and age-dependent usage probabilities until the
    net-retention counter runs out, and the net is discarded.

    While **SimpleBednet** usage is applied as a daily reduction in efficacy,
    **UsageDependentBednet** uses the usage efficacy to determine whether the person
    slept under the net that night.

    For example, consider a bednet configured with 0% repelling, 100% blocking, 100% killing,
    and 50% usage effect. A person with a **SimpleBednet** will have a net with final efficacy
    of 50% blocking and 50% killing every night. A person with a **UsageDependentBednet** will
    have half of their nights with a 100% blocking and 100% killing net and half with no net
    usage at all.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target sub-groups using genomes, especially specific species.
    * Time-based expiration: Yes, an expiration timer independent from waning effects can be
      configured.
    * Purge existing: Yes. A new bednet replaces any other bednet intervention.
    * Vector killing contributes to: Indoor Die Before Feeding
    * Vector effects: Repelling, blocking, and killing
    * Vector sexes affected: Indoor meal-seeking females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the bednet's mosquito repelling effect. This is the first effect applied
            to meal-seeking mosquitoes that encounter the net. Repelled vectors do not enter the netted space —
            they survive and do not attempt to feed again until the following day and are not affected by the
            blocking or killing effects.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        blocking_config (AbstractWaningConfig, required):
            Waning effect configuration for the bednet's ability to block meal-seeking mosquito. The blocking_config
            probabilities are applied to the subset of meal-seeking mosquitoes that have not been repelled.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            Waning effect configuration for the bednet's insecticidal killing effect. For meal-seeking vector to be
            affected, it must be successfully blocked first, mimicking mosquito landing on the bednet,
            so killing_config probabilities are applied to the subset of mosquitoes that are blocked.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        usage_config_list (list[AbstractWaningConfig], optional):
            A list of waning effect configurations that combine to determine whether a net owner sleeps
            under the net on a given night. Each waning effect in the list produces a value between 0 and 1,
            and the product of all values is the probability that the person uses the net that night. This
            allows combining independent usage factors such as age-dependent and seasonal usage patterns.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).
            Default value: None

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        received_event (str, optional):
            An individual-level event to broadcast when a bednet is received.
            Default value: None

        using_event (str, optional):
            An individual-level event to broadcast when a bednet is being used that night.
            Default value: None

        discard_event (str, optional):
            An individual-level event to broadcast when a bednet is discarded.
            Default value: None

        expiration_period_distribution(BaseDistribution, required):
            The distribution type to use for setting the expiration of the intervention. Each intervention gets
            an expiration duration by doing a random draw from the distribution.  Please use the following
            distribution classes from emodpy_malaria.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 blocking_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 expiration_period_distribution: BaseDistribution,
                 usage_config_list: list[AbstractWaningConfig] = None,
                 insecticide_name: str = None,
                 received_event: str = None,
                 using_event: str = None,
                 discard_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'UsageDependentBednet', common_intervention_parameters)

        self._intervention.Blocking_Config = blocking_config.to_schema_dict(campaign)
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)

        if usage_config_list is not None:
            self._intervention.Usage_Config_List = [uc.to_schema_dict(campaign) for uc in usage_config_list]
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))
        if received_event is not None:
            self._intervention.Received_Event = set_event(received_event, 'received_event', campaign, False)
        if using_event is not None:
            self._intervention.Using_Event = set_event(using_event, 'using_event', campaign, False)
        if discard_event is not None:
            self._intervention.Discard_Event = set_event(discard_event, 'discard_event', campaign, False)
        if not isinstance(expiration_period_distribution, BaseDistribution):
            raise ValueError(f"'expiration_period_distribution' must be an instance of BaseDistribution, not {type(expiration_period_distribution)}.")
        self.set_distribution(expiration_period_distribution, 'Expiration_Period')


class MultiInsecticideUsageDependentBednet(IndividualIntervention):
    """
    The **MultiInsecticideUsageDependentBednet** intervention class is similar to
    [UsageDependentBednet](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/) but allows
    the addition of multiple insecticides. Each insecticide entry defines its own repelling,
    blocking, and killing waning effects. The effectiveness of multiple insecticides is combined
    using the following equation::

        Total efficacy = 1.0 - (1.0 - efficacy_1) * (1.0 - efficacy_2) * ... * (1.0 - efficacy_n)

    As in **UsageDependentBednet**, bednet ownership and nightly bednet usage are distinct. Net
    ownership is configured through the demographic coverage, and the repelling, blocking, and
    killing rates of mosquitoes are time-dependent. Nightly use of bednets is age-dependent and
    can vary seasonally. Once a net has been distributed to someone, the nightly net usage is
    determined by the product of the waning effects in the usage_config_list until the expiration
    timer runs out and the net is discarded.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target specific species or other subgroups.
    * Time-based expiration: Yes, an expiration timer independent from waning effects can be
      configured.
    * Purge existing: Yes. A new bednet replaces any other bednet intervention.
    * Vector killing contributes to: Indoor Die Before Feeding
    * Vector effects: Repelling, blocking, killing
    * Vector sexes affected: Indoor meal-seeking females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffect], required):
            A list of
            [InsecticideWaningEffect](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/)
            objects with repelling, blocking, and killing configs (variant ``"RBK"``), each
            defining the repelling, blocking, and killing waning effects and
            insecticide name for one insecticide. The total efficacy across insecticides is
            combined as
            ``1 - (1 - efficacy_1) * (1 - efficacy_2) * ... * (1 - efficacy_n)``.
            Only relevant when modeling insecticide resistance via the vector genetics
            system. The insecticide name in each entry must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a
            vector encounters this intervention, the insecticide's killing, blocking, and
            repelling effects are modified based on the vector's genotype and the resistance
            modifiers configured for that insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.

        usage_config_list (list[AbstractWaningConfig], optional):
            A list of waning effect configurations that combine to determine whether a net owner sleeps
            under the net on a given night. Each waning effect in the list produces a value between 0 and 1,
            and the product of all values is the probability that the person uses the net that night. This
            allows combining independent usage factors such as age-dependent and seasonal usage patterns.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).
            Default value: None

        received_event (str, optional):
            An individual-level event to broadcast when a bednet is received.
            Default value: None

        using_event (str, optional):
            An individual-level event to broadcast when a bednet is being used that night.
            Default value: None

        discard_event (str, optional):
            An individual-level event to broadcast when a bednet is discarded.
            Default value: None

        expiration_period_distribution(BaseDistribution, required):
            The distribution type to use for setting the expiration of the intervention. Each intervention gets
            an expiration duration by doing a random draw from the distribution.  Please use the following
            distribution classes from emodpy_malaria.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list[InsecticideWaningEffect],
                 expiration_period_distribution: BaseDistribution,
                 usage_config_list: list[AbstractWaningConfig] = None,
                 received_event: str = None,
                 using_event: str = None,
                 discard_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideUsageDependentBednet', common_intervention_parameters)

        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffect):
                raise ValueError(
                    f"'insecticides[{i}]' must be an InsecticideWaningEffect instance, "
                    f"got {type(ins).__name__}.")
            ins.require_variant("RBK", "MultiInsecticideUsageDependentBednet")
        self._intervention.Insecticides = [ins.to_schema_dict() for ins in insecticides]
        for ins in insecticides:
            if ins._insecticide_name is not None:
                campaign.implicits.append(partial(
                    validate_insecticide_name, insecticide_name=ins._insecticide_name,
                    intervention_name='MultiInsecticideUsageDependentBednet'))
        if usage_config_list is not None:
            self._intervention.Usage_Config_List = [uc.to_schema_dict(campaign) for uc in usage_config_list]
        if received_event is not None:
            self._intervention.Received_Event = set_event(received_event, 'received_event', campaign, False)
        if using_event is not None:
            self._intervention.Using_Event = set_event(using_event, 'using_event', campaign, False)
        if discard_event is not None:
            self._intervention.Discard_Event = set_event(discard_event, 'discard_event', campaign, False)
        if not isinstance(expiration_period_distribution, BaseDistribution):
            raise ValueError(f"'expiration_period_distribution' must be an instance of BaseDistribution, not {type(expiration_period_distribution)}.")
        self.set_distribution(expiration_period_distribution, 'Expiration_Period')


class IRSHousingModification(IndividualIntervention):
    """
    The **IRSHousingModification** intervention class includes Indoor Residual Spraying (IRS)
    in the simulation. IRS is another key vector control tool in which insecticide is sprayed on
    the interior walls of a house so that mosquitoes resting on the walls after consuming a
    blood meal will die. This intervention affects indoor meal-seeking mosquitoes, which may be repelled from
    entering the house or killed after landing on the wall post-meal. Since this intervention does not kill vectors
    before feeding, infectious vectors that are not repelled and die from this intervention still contribute to malaria
    transmission by potentially passing it to humans before they die.

    Note that EMOD does not explicitly model houses. **IRSHousingModification** is distributed to
    individuals, which means you can give IRS to some people in the population and not others —
    it does not apply uniformly to all individuals in a node the way a node-level intervention
    would. Also, because this intervention is tied to the individual, when the individual migrates,
    they "take" it with them. We have a node-level ``IndoorSpaceSpraying`` intervention that is distributed
    to nodes and does not migrate with individuals but rather affects the individuals currently in the node.


    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target specific species or other subgroups.
    * Time-based expiration: No
    * Purge existing: No. Existing interventions of this class continue to exist together
      with new ones. Efficacies combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: Indoor Die After Feeding
    * Vector effects: Repelling and killing
    * Vector sexes affected: Indoor meal-seeking females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the IRS repelling efficacy. Repelled vectors survive and do not attempt
            to feed again until the following day and are not affected by the killing effect of IRS.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            Waning effect configuration for the IRS killing efficacy. The killing effect is applied to indoor
            meal-seeking vectors that have not been repelled, mimicking mosquitoes landing on the wall and being
            exposed to the insecticide after the meal.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'IRSHousingModification', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class MultiInsecticideIRSHousingModification(IndividualIntervention):
    """
    The **MultiInsecticideIRSHousingModification** intervention class is an individual-level
    intervention that builds on
    [IRSHousingModification](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/) by
    enabling the use of multiple insecticides. The killing efficacy of each insecticide can be
    specified. This class uses Indoor Residual Spraying (IRS), where insecticide is sprayed on
    the interior walls of houses such that mosquitoes resting on the walls after consuming
    blood meals will die. The effectiveness of the intervention is combined using the following
    equation::

        Total efficacy = 1.0 - (1.0 - efficacy_1) * (1.0 - efficacy_2) * ... * (1.0 - efficacy_n)

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target specific species or other subgroups.
    * Time-based expiration: No
    * Purge existing: No. Existing interventions of this class continue to exist together
      with new ones. Efficacies combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: Indoor Die After Feeding, Indoor Die Before Feeding
      (when combined with HostSeekingSugarTrap)
    * Vector effects: Repelling and killing
    * Vector sexes affected: Females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffect], required):
            A list of
            [InsecticideWaningEffect](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/)
            objects with repelling and killing configs (variant ``"RK"``), each defining the
            repelling and killing waning effects and insecticide name for one insecticide.
            The total efficacy across insecticides is combined as
            ``1 - (1 - efficacy_1) * (1 - efficacy_2) * ... * (1 - efficacy_n)``.
            Only relevant when modeling insecticide resistance via the vector genetics
            system. The insecticide name in each entry must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a
            vector encounters this intervention, the insecticide's killing, blocking, and
            repelling effects are modified based on the vector's genotype and the resistance
            modifiers configured for that insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list[InsecticideWaningEffect],
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideIRSHousingModification', common_intervention_parameters)

        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffect):
                raise ValueError(
                    f"'insecticides[{i}]' must be an InsecticideWaningEffect instance, "
                    f"got {type(ins).__name__}.")
            ins.require_variant("RK", "MultiInsecticideIRSHousingModification")
        self._intervention.Insecticides = [ins.to_schema_dict() for ins in insecticides]
        for ins in insecticides:
            if ins._insecticide_name is not None:
                campaign.implicits.append(partial(
                    validate_insecticide_name, insecticide_name=ins._insecticide_name,
                    intervention_name='MultiInsecticideIRSHousingModification'))


class _SimpleHousingModification(IndividualIntervention):
    """
    The **SimpleHousingModification** intervention class implements a generic housing
    modification for vector control.

    Note: It is the base class from which other housing
    modifications are derived. This intervention is not used in simulations directly, and is here for the
    purpose of documentation completeness.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, when it has been distributed to individuals.
    * Uses insecticides: Yes. The vector genome can be used to target specific vectors.
    * Time-based expiration: No. It will continue to exist even if efficacy is zero.
    * Purge existing: No. Existing interventions of this class continue to exist together
      with new ones. Efficacies combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: Die Before Feeding, Die After Feeding, Host Not
      Available
    * Vector effects: Repelling, killing
    * Vector sexes affected: Indoor meal-seeking females
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the IRS repelling efficacy. Repelled vectors survive and do not attempt
            to feed again until the following day and are not affected by the killing effect of IRS.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            Waning effect configuration for the IRS killing efficacy. The killing effect is applied to indoor
            meal-seeking vectors that have not been repelled, mimicking mosquitoes landing on the wall and being
            exposed to the insecticide after the meal.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SimpleHousingModification', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class ScreeningHousingModification(IndividualIntervention):
    """
    The **ScreeningHousingModification** intervention class implements housing screens as a
    vector control effort. Housing screens are used to decrease the number of mosquitoes that
    can enter indoors and therefore reduce indoor biting. The vectors that are not repelled by the screens and
    enter the house might then be killed post-meal from landing on the screen.

    This intervention works similarly to IRS. Like **IRSHousingModification**, it is distributed
    to individuals rather than applied to a node — EMOD does not explicitly model houses, so
    this intervention can be given to a subset of the population to represent screened households.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target specific species or other subgroups.
    * Time-based expiration: No
    * Purge existing: Yes and No. A new intervention of this class will overwrite any
      existing intervention of the same class with the same Intervention_Name. If
      Intervention_Name is different, both interventions will coexist and their efficacies
      will combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: Die Indoor After Feeding, Die Indoor Before Feeding
    * Vector effects: Repelling and killing
    * Vector sexes affected: Indoor meal-seeking females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the screen repelling efficacy. Repelled vectors survive and do not attempt
            to feed again until the following day and are not affected by the killing effect of the screen.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            Waning effect configuration for the screen killing efficacy. The killing effect is applied to indoor
            meal-seeking vectors that have not been repelled, mimicking mosquitoes landing on the screen and being
            exposed to the insecticide after the meal.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'ScreeningHousingModification', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class SpatialRepellentHousingModification(IndividualIntervention):
    """
    The **SpatialRepellentHousingModification** intervention class is a housing modification
    utilizing spatial repellents. The protection provided by this intervention is exclusively
    against indoor-biting mosquitoes. This intervention is similar to **IRSHousingModification** and
    **ScreeningHousingModification**, but it only has a repelling effect without a killing effect. Repelled vectors
    survive and do not attempt to feed again until the following day.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, when it has been distributed to individuals.
    * Uses insecticides: Yes. The vector genome can be used to target specific vectors.
    * Time-based expiration: No. It will continue to exist even if efficacy is zero.
    * Purge existing: No. Existing interventions continue to exist together with new ones.
      Efficacies combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: No killing
    * Vector effects: Repelling
    * Vector sexes affected: Indoor meal-seeking females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the IRS repelling efficacy. Repelled vectors survive and do not attempt
            to feed again until the following day and are not affected by the killing effect of IRS.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SpatialRepellentHousingModification', common_intervention_parameters)

        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class SimpleIndividualRepellent(IndividualIntervention):
    """
    The **SimpleIndividualRepellent** intervention class provides protection to individuals
    against both indoor-feeding and outdoor-feeding mosquito bites.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, when it has been distributed to individuals.
    * Uses insecticides: Yes. The vector genome can be used to target specific vectors.
    * Time-based expiration: No. It will continue to exist even if efficacy is zero.
    * Purge existing: Yes and No. A new intervention of this class will overwrite any
      existing intervention of the same class with the same Intervention_Name. If
      Intervention_Name is different, both interventions will coexist and their efficacies
      will combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: No killing
    * Vector effects: Repelling
    * Vector sexes affected: All meal-seeking females
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the IRS repelling efficacy. Repelled vectors survive and do not attempt
            to feed again until the following day and are not affected by the killing effect of IRS.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SimpleIndividualRepellent', common_intervention_parameters)

        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class IndoorIndividualEmanator(IndividualIntervention):
    """
    The **IndoorIndividualEmanator** intervention class is a house modification intervention
    that imitates the use of personal mosquito repellents designed for indoor use, such as
    mosquito coils or vaporizer mats. These interventions release insecticides into the air to
    repel or kill mosquitoes in the vicinity of the individual using the emanator. The
    intervention is distributed to individuals, allowing for targeting specific subgroups of
    the population.

    The intervention acts on female vectors seeking a blood meal indoors. Once the vector is
    indoors, it is first repelled based on the repelling effect. Then, vectors that are not
    repelled are subjected to the killing effect. Vectors that are not repelled or killed can
    proceed to try to bite the individual and will be subject to other individual indoor
    interventions. After the vectors have successfully fed (human or non-human meal), they are
    subjected again to the killing effect of the emanator before exiting the indoor
    environment. Hence, the **IndoorIndividualEmanator** can contribute to both Indoor Die
    Before Feeding and Indoor Die After Feeding.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target specific species or other subgroups.
    * Time-based expiration: No
    * Purge existing: No. Existing interventions continue to exist together with new ones.
      Efficacies combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: Indoor Die Before Feeding, Indoor Die After Feeding
    * Vector effects: Repelling and killing
    * Vector sexes affected: Females seeking blood meal indoors only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            Waning effect configuration for the emanator repelling efficacy. Repelled vectors survive and do not attempt
            to feed again until the following day and are not affected by the killing effect of the emanator.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            Waning effect configuration for the emanator killing efficacy. The killing effect is applied to indoor
            meal-seeking vectors that have not been repelled by the emanator, mimicking mosquitoes flying through
            toxic smoke. The killing effect is applied before and, again, after feeding.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'IndoorIndividualEmanator', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class HumanHostSeekingTrap(IndividualIntervention):
    """
    The **HumanHostSeekingTrap** intervention class applies a trap that attracts and kills
    indoor host-seeking mosquitoes in the simulation. Human-host-seeking traps are
    individually-distributed interventions that have attraction and killing rates that decay
    in an analogous fashion to the killing rates of bednets.

    An artificial diet diverts the vector from feeding on the indoor human, resulting in a
    two-fold benefit: (1) uninfected mosquitoes avoid biting infected humans some of the time,
    therefore decreasing the amount of human-to-vector transmission, and (2) infectious vectors
    are diverted to feed on an artificial diet instead of humans, therefore decreasing the
    amount of vector-to-human transmission.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: No
    * Time-based expiration: No
    * Purge existing: Yes. A new intervention of this class will replace an existing one.
    * Vector killing contributes to: Indoor Die Before Feeding
    * Vector effects: Artificial Diet feed instead of Human or Animal Feed
    * Vector sexes affected: Females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        attract_config (AbstractWaningConfig, required):
            Waning effect for the trap's attractiveness. The vectors that are attracted to the trap will
            feed on an artificial diet instead of humans, and therefore do not contribute to malaria transmission
            this feeding cycle. Out of the vectors that are attacted to the trap, some will die due to the killing
            effect defined by the **killing_config**.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            Waning effect configuration for the trap killing efficacy. The killing effect is applied to indoor
            meal-seeking vectors that have been attracted to the trap.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 attract_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HumanHostSeekingTrap', common_intervention_parameters)

        self._intervention.Attract_Config = attract_config.to_schema_dict(campaign)
        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)


class Ivermectin(IndividualIntervention):
    """
    The **Ivermectin** intervention class modifies the feeding outcome probabilities for both
    indoor- and outdoor-feeding mosquitoes. Ivermectin works by increasing the mortality of
    mosquitoes after they blood-feed on a human. It is an individually-distributed intervention
    that configures the waning of the drug's killing effect on the adult mosquito population.
    This intervention enables exploration of the impact of giving humans an insecticidal drug,
    and how the effectiveness and duration of the drug's killing effect interacts with other
    interventions. For example, you can look at the impact of controlling and eliminating
    malaria transmission using both anti-parasite drugs that clear existing infections and
    insecticidal drugs.

    At a glance:

    * Distributed to: Individuals
    * Serialized: Yes, if it has been distributed to a person.
    * Uses insecticides: Yes. Can target specific species or other subgroups.
    * Time-based expiration: No, but expires if efficacy is below 0.00001.
    * Purge existing: No. Existing interventions of this class continue to exist together
      with new ones. Efficacies combine as 1-(1-prob1)*(1-prob2).
    * Vector killing contributes to: Indoor/Outdoor Die After Feeding
    * Vector effects: Killing
    * Vector sexes affected: Meal-seeking females only
    * Vector life stage affected: Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            Waning effect for ivermectin's mosquito-killing efficacy for vectors who have had a blood meal from
            the treated human. The killing effect is applied after the blood meal, and therefore does not prevent
            infectious mosquitoes from infecting the human host or getting infected by an infectious human, but
            it does prevent them from spreading the infection any further.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'Ivermectin', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class _RTSSVaccine(IndividualIntervention):
    """
    Deprecated: **_RTSSVaccine** is not actively used or maintained. Use
    `ControlledVaccine` or `SimpleVaccine` instead for vaccine interventions.

    The **_RTSSVaccine** intervention class protects individuals against infection acquisition
    by directly boosting the circumsporozoite protein (CSP) antibody concentration. This
    contrasts with the SimpleVaccine intervention, which is used to modify the probability of
    acquisition, transmission, or death.

    The CSP antibody reduces the probability that sporozoites survive to infect the
    liver/hepatocytes. A higher boosted_antibody_concentration means the person will be less
    likely to have sporozoites survive and infect the hepatocytes. Without the vaccine, CSP
    does not do anything. The following parameters impact CSP and its sporozoite
    killing ability: **Antibody_CSP_Killing_Threshold**,
    **Antibody_CSP_Killing_Inverse_Width**, and **Antibody_CSP_Decay_Days** (set via
    ``malaria_config.set_team_defaults()`` or directly on ``config.parameters``).

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        boosted_antibody_concentration (float, optional):
            The antibody concentration level to boost to upon vaccination.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 boosted_antibody_concentration: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'RTSSVaccine', common_intervention_parameters)  # noqa: internal class name unchanged

        self._intervention.Boosted_Antibody_Concentration = validate_value_range(
            boosted_antibody_concentration, 'boosted_antibody_concentration', 0, 3.40282e+38, float)


class BitingRisk(IndividualIntervention):
    """
    The **BitingRisk** class allows you to adjust the relative risk that the person is bitten
    by a vector. As an intervention, it allows you to target specific groups at specific times
    during the simulation.

    The relative risk is population-relative: it controls how likely one individual is to be
    bitten *compared to others in the same node*, not the absolute biting rate of the node.
    For example, setting the entire population to a relative risk of 10 has no effect because
    everyone's risk is equally scaled — the ratio between individuals is unchanged. The relative
    risk is only meaningful when some individuals have a different value than others.

    The relative biting rate can be initially set using
    [MalariaDemographics.set_risk_distribution()](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/demographics/MalariaDemographics/),
    which gives each new person their own relative risk at their inception.

    The relative biting rate can be thought of as having two parts: the relative risk value
    and the age dependent value. Age dependence is set using
    ``config.parameters.Age_Dependent_Biting_Risk_Type`` (set to
    ``AgeDependentBitingRiskType.LINEAR`` or
    ``AgeDependentBitingRiskType.SURFACE_AREA_DEPENDENT``; ``AgeDependentBitingRiskType.OFF``
    disables it). These two values (from age dependence and
    relative risk) are multiplied to get the resulting rate, which is then used to control how
    much contagion is deposited from an infectious individual and the probability that an
    infection is acquired.

    This intervention expires. To reset it, distribute another **BitingRisk** intervention
    that sets it back to the original value. Note that this is a relative biting rate. For
    example, giving everyone a value of 10 is the same as giving everyone a value of 1. This
    intervention is used to indicate some individuals are more likely to be bitten than others.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        risk_distribution(BaseDistribution, required):
            The distribution type to use for assigning the relative risk of being bitten by a mosquito to
            each individual. Each assigned value is a random draw from the distribution. Please use the following
            distribution classes from emodpy_malaria.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 risk_distribution: BaseDistribution,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'BitingRisk', common_intervention_parameters)

        if not isinstance(risk_distribution, BaseDistribution):
            raise ValueError(f"'risk_distribution' must be an instance of BaseDistribution, not {type(risk_distribution)}.")
        self.set_distribution(risk_distribution, 'Risk')


class SimpleHealthSeekingBehavior(IndividualIntervention):
    """
    The **SimpleHealthSeekingBehavior** intervention class models the time delay that typically
    occurs between when an individual experiences onset of symptoms and when they seek help
    from a health care provider. Several factors may contribute to such delays including
    accessibility, cost, and trust in the health care system. This intervention models this
    time delay as an exponential process; at every time step, the model draws randomly to
    determine if the individual will receive the specified intervention. As an example, this
    intervention can be nested in a **NodeLevelHealthTriggeredIV** so that when an individual
    is infected or experiences clinical symptoms, they receive a **SimpleHealthSeekingBehavior**,
    representing that the individual will now seek care. The individual subsequently seeks care with an
    exponentially distributed delay and ultimately receives the specified intervention.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        tendency (float, optional):
            Probability that the individual will seek care.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        single_use (bool, optional):
            If True, the intervention expires after first use, set to False, it remains active indefinitely.
            Default value: True

        actual_intervention (Union[str, IndividualIntervention], required):
            The action to take when the individual seeks care. If a string, it is broadcast
            as an individual-level event. If an ``IndividualIntervention``, it is distributed
            to the individual.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None

    Example:
        Distribute antimalarial treatment when symptomatic individuals seek care::

            from emodpy_malaria.campaign.individual_intervention import SimpleHealthSeekingBehavior, AntimalarialDrug

            hsb = SimpleHealthSeekingBehavior(
                campaign=campaign,
                tendency=0.8,
                single_use=False,
                actual_intervention=AntimalarialDrug(campaign, drug_type="Chloroquine")
            )

    Example:
        Broadcast an event when care is sought::

            from emodpy_malaria.campaign.individual_intervention import SimpleHealthSeekingBehavior

            hsb = SimpleHealthSeekingBehavior(
                campaign=campaign,
                tendency=0.6,
                actual_intervention="SeekingTreatment"
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 actual_intervention: Union[str, IndividualIntervention],
                 tendency: float = 1,
                 single_use: bool = True,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SimpleHealthSeekingBehavior', common_intervention_parameters)

        self._intervention.Tendency = validate_value_range(tendency, 'tendency', 0, 1, float)
        self._intervention.Single_Use = 1 if single_use else 0

        if isinstance(actual_intervention, str):
            self._intervention.Event_Or_Config = EventOrConfig.Event
            self._intervention.Actual_IndividualIntervention_Event = set_event(
                actual_intervention, 'actual_intervention', campaign, False)
        elif isinstance(actual_intervention, IndividualIntervention):
            self._intervention.Event_Or_Config = EventOrConfig.Config
            self._intervention.Actual_IndividualIntervention_Config = actual_intervention.to_schema_dict()
        else:
            raise ValueError(
                f"'actual_intervention' must be a string (event to be broadcast) or an IndividualIntervention, "
                f"got {type(actual_intervention).__name__}.")


class OutbreakIndividualMalariaGenetics(IndividualIntervention):
    """
    The **OutbreakIndividualMalariaGenetics** intervention class creates an outbreak with a specific
    malaria parasite genome (barcode, drug resistance alleles, HRP markers). This intervention is
    part of the Full Parasite Genetics (FPG) model. See
    [Full Parasite Genetics (FPG) Model](https://emod.idmod.org/emodpy-malaria/emod/malaria-model-fpg/) for details.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        create_nucleotide_sequence_from (NucleotideSequenceOrigin, required):
            Determines how the parasite genome is created. Use the
            [NucleotideSequenceOrigin](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) enum values:

            * ``NucleotideSequenceOrigin.BARCODE_STRING`` -- Create the genome from
              **barcode_string**, **drug_resistant_string**, and **hrp_string**.
              The barcode locations are defined in the config via
              ``malaria_config.set_parasite_genetics_params()``. Everyone who receives this
              outbreak intervention gets the same barcode values. It is assumed that if a person
              has had an infection with a particular barcode, they have antibodies to fight a new
              infection with the same barcode. Use multiple distributions with different barcode
              strings to achieve infection diversity.
            * ``NucleotideSequenceOrigin.ALLELE_FREQUENCIES`` -- Each new infection from
              this outbreak gets a genome created randomly from allele frequencies defined
              via **barcode_allele_frequencies_per_genome_location**,
              **drug_resistant_allele_frequencies_per_genome_location**, and
              **hrp_allele_frequencies_per_genome_location**. This allows
              random creation of new genomes with controlled allele frequencies. Note that you
              need to distribute many infections for the population-level allele frequencies to
              reflect the configured values — distributing only a handful of infections will
              not reliably reproduce the intended frequency distribution. After the outbreak,
              new genomes are only created via meiosis and recombination.
            * ``NucleotideSequenceOrigin.NUCLEOTIDE_SEQUENCE`` -- Use a fully specified
              nucleotide sequence, including MSP and major epitope values. This requires
              **barcode_string**, **drug_resistant_string**, **hrp_string**,
              **msp_variant_value**, and **pfemp1_variants_values** to all be specified.

        barcode_string (str, conditionally required):
            A series of nucleotide base letters (A, C, G, T) that represent the values at
            barcode locations in the parasite genome. The length of the string depends on
            the number of barcode locations configured via
            ``malaria_config.set_parasite_genetics_params()``. Each character corresponds to one
            location, and locations are assumed to be in ascending order. Required when
            **create_nucleotide_sequence_from** is set to ``NUCLEOTIDE_SEQUENCE`` or
            ``BARCODE_STRING``.
            Default value: None

        drug_resistant_string (str, optional):
            A series of nucleotide base letters (A, C, G, T) that represent the values at
            drug-resistance locations in the parasite genome. The length of the string
            depends on the number of locations defined in the drug-resistance locations configured via
            ``malaria_config.set_parasite_genetics_params()``. Each character
            corresponds to one location, and locations are assumed to be in ascending order.
            Required when **create_nucleotide_sequence_from** is set to
            ``NUCLEOTIDE_SEQUENCE`` or ``BARCODE_STRING``.
            Default value: None

        hrp_string (str, optional):
            A series of nucleotide base letters (A, C, G, T) that represent HRP
            (histidine-rich protein) values at locations in the parasite genome. The length
            of the string depends on the number of locations defined in the
            HRP locations configured via
            ``malaria_config.set_parasite_genetics_params()``. An
            ``A`` means the HRP marker is not present; any other nucleotide (``C``, ``G``,
            ``T``) means it is present. Required when **create_nucleotide_sequence_from**
            is set to ``NUCLEOTIDE_SEQUENCE`` or ``BARCODE_STRING``.
            Default value: None

        barcode_allele_frequencies_per_genome_location (list[list[float]], optional):
            The fractions of allele occurrences for each location in the barcode. This 2D
            array has an inner array for each location in the barcode. The number of inner
            arrays depends on the number of barcode locations configured via
            ``malaria_config.set_parasite_genetics_params()``. Each inner array should
            have four values for the frequency of each allele at that location. The position
            of the value in the inner array determines the allele: index 0 is A, index 1 is
            C, index 2 is G, and index 3 is T. The four values in each inner array must sum
            to 1.0. Required when **create_nucleotide_sequence_from** is set to
            ``ALLELE_FREQUENCIES``.
            Range per value: 0.0 to 1.0.
            Default value: None

        drug_resistant_allele_frequencies_per_genome_location (list[list[float]], optional):
            The fractions of allele occurrences for each drug-resistance location. This 2D
            array has an inner array for each location. The number of inner arrays depends
            on the number of drug-resistance locations configured via
            ``malaria_config.set_parasite_genetics_params()``. Each inner array should have four
            values for the frequency of each allele at that location. The position of the
            value in the inner array determines the allele: index 0 is A, index 1 is C,
            index 2 is G, and index 3 is T. Required when
            **create_nucleotide_sequence_from** is set to ``ALLELE_FREQUENCIES``.
            Range per value: 0.0 to 1.0.
            Default value: None

        hrp_allele_frequencies_per_genome_location (list[list[float]], optional):
            The fractions of allele occurrences for each HRP location. This 2D array has
            an inner array for each location. The number of inner arrays depends on the
            number of HRP locations configured via
            ``malaria_config.set_parasite_genetics_params()``. Each inner array should have
            four values for the
            frequency of each allele at that location. The position of the value in the
            inner array determines the allele: index 0 is A, index 1 is C, index 2 is G,
            and index 3 is T. Required when **create_nucleotide_sequence_from** is set to
            ``ALLELE_FREQUENCIES``. Range per value: 0.0 to 1.0.
            Default value: None

        msp_variant_value (int, conditionally required):
            The Merozoite Surface Protein (MSP) variant value used to determine how
            antibodies recognize merozoites during blood-stage infection. This value must
            be less than or equal to the ``Falciparum_MSP_Variants`` value set via
            ``malaria_config.set_parasite_genetics_params()``. Can only be used when **create_nucleotide_sequence_from** is set to
            ``NUCLEOTIDE_SEQUENCE``.
            Default value: None

        pfemp1_variants_values (list[int], optional):
            The PfEMP1 (Plasmodium falciparum Erythrocyte Membrane Protein 1) variant
            values, also known as major epitopes, used to define how antibodies recognize
            infected red blood cells. Each value in the array must be less than or equal
            to the ``Falciparum_PfEMP1_Variants`` value set via
            ``malaria_config.set_parasite_genetics_params()``. The array must
            contain exactly 50 values. Only used when **create_nucleotide_sequence_from**
            is set to ``NUCLEOTIDE_SEQUENCE``.
            Default value: None

        ignore_immunity (bool, optional):
            If True, individuals will be force-infected with the specified parasite strain
            regardless of their actual immunity level. If False, individual's immunity
            affects whether the infection takes hold.
            Default value: True

        incubation_period_override (int, optional):
            The incubation period, in days, that infected individuals go through before
            becoming infectious. This overrides the incubation period set in the
            configuration file. Set to -1 to use the default incubation period.
            Range: -1 to 2147480000.
            Default value: -1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None

    Example:
        Create an outbreak with a specific barcode::

            from emodpy_malaria.campaign.individual_intervention import OutbreakIndividualMalariaGenetics
            from emodpy_malaria.utils.emod_enum import NucleotideSequenceOrigin

            outbreak = OutbreakIndividualMalariaGenetics(
                campaign=campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
                barcode_string="AATTCCGG",
                drug_resistant_string="AA",
                hrp_string="AT"
            )

    Example:
        Create an outbreak using allele frequencies::

            from emodpy_malaria.campaign.individual_intervention import OutbreakIndividualMalariaGenetics
            from emodpy_malaria.utils.emod_enum import NucleotideSequenceOrigin

            outbreak = OutbreakIndividualMalariaGenetics(
                campaign=campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                barcode_allele_frequencies_per_genome_location=[
                    [0.25, 0.25, 0.25, 0.25],  # location 1
                    [0.50, 0.50, 0.00, 0.00],  # location 2
                ],
                ignore_immunity=False
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 create_nucleotide_sequence_from: NucleotideSequenceOrigin,
                 barcode_string: str = None,
                 drug_resistant_string: str = None,
                 hrp_string: str = None,
                 barcode_allele_frequencies_per_genome_location: list[list[float]] = None,
                 drug_resistant_allele_frequencies_per_genome_location: list[list[float]] = None,
                 hrp_allele_frequencies_per_genome_location: list[list[float]] = None,
                 msp_variant_value: int = None,
                 pfemp1_variants_values: list[int] = None,
                 ignore_immunity: bool = True,
                 incubation_period_override: int = -1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OutbreakIndividualMalariaGenetics', common_intervention_parameters)
        campaign.implicits.append(partial(
            validate_malaria_model,
            intervention_name="OutbreakIndividualMalariaGenetics"))

        _location_checks = [
            (barcode_string,
             'barcode_string', 'Barcode_Genome_Locations'),
            (drug_resistant_string,
             'drug_resistant_string', 'Drug_Resistant_Genome_Locations'),
            (hrp_string,
             'hrp_string', 'HRP_Genome_Locations'),
            (barcode_allele_frequencies_per_genome_location,
             'barcode_allele_frequencies_per_genome_location', 'Barcode_Genome_Locations'),
            (drug_resistant_allele_frequencies_per_genome_location,
             'drug_resistant_allele_frequencies_per_genome_location', 'Drug_Resistant_Genome_Locations'),
            (hrp_allele_frequencies_per_genome_location,
             'hrp_allele_frequencies_per_genome_location', 'HRP_Genome_Locations'),
        ]
        for _value, _pname, _lattr in _location_checks:
            if _value is not None:
                campaign.implicits.append(partial(
                    validate_genome_locations_length,
                    value=_value, param_name=_pname, locations_attr=_lattr))

        self._intervention.Ignore_Immunity = 1 if ignore_immunity else 0
        self._intervention.Incubation_Period_Override = incubation_period_override

        string_params = {
            "barcode_string": barcode_string,
            "drug_resistant_string": drug_resistant_string,
            "hrp_string": hrp_string,
        }
        allele_freq_params = {
            "barcode_allele_frequencies_per_genome_location": barcode_allele_frequencies_per_genome_location,
            "drug_resistant_allele_frequencies_per_genome_location": drug_resistant_allele_frequencies_per_genome_location,
            "hrp_allele_frequencies_per_genome_location": hrp_allele_frequencies_per_genome_location,
        }
        nucleotide_seq_params = {
            "msp_variant_value": msp_variant_value,
            "pfemp1_variants_values": pfemp1_variants_values,
        }

        mode = create_nucleotide_sequence_from
        mode_name = mode.value

        if mode in (NucleotideSequenceOrigin.BARCODE_STRING, NucleotideSequenceOrigin.NUCLEOTIDE_SEQUENCE):
            if barcode_string is None:
                raise ValueError(
                    f"'barcode_string' is required when 'create_nucleotide_sequence_from' "
                    f"is set to {mode_name}.")
            for name, value in allele_freq_params.items():
                if value is not None:
                    raise ValueError(
                        f"'{name}' can only be used when 'create_nucleotide_sequence_from' "
                        f"is set to ALLELE_FREQUENCIES, got {mode_name}.")

        if mode == NucleotideSequenceOrigin.NUCLEOTIDE_SEQUENCE:
            if pfemp1_variants_values is None or len(pfemp1_variants_values) != 50:
                count = len(pfemp1_variants_values) if pfemp1_variants_values is not None else 0
                raise ValueError(
                    f"'pfemp1_variants_values' must contain exactly 50 values (got "
                    f"{count}), and is required when "
                    f"create_nucleotide_sequence_from is NUCLEOTIDE_SEQUENCE.")

        if mode == NucleotideSequenceOrigin.BARCODE_STRING:
            for name, value in nucleotide_seq_params.items():
                if value is not None:
                    raise ValueError(
                        f"'{name}' can only be used when 'create_nucleotide_sequence_from' "
                        f"is set to NUCLEOTIDE_SEQUENCE, got {mode_name}.")

        if mode == NucleotideSequenceOrigin.ALLELE_FREQUENCIES:
            for name, value in string_params.items():
                if value is not None:
                    raise ValueError(
                        f"'{name}' can only be used when 'create_nucleotide_sequence_from' "
                        f"is set to BARCODE_STRING or NUCLEOTIDE_SEQUENCE, got {mode_name}.")
            for name, value in nucleotide_seq_params.items():
                if value is not None:
                    raise ValueError(
                        f"'{name}' can only be used when 'create_nucleotide_sequence_from' "
                        f"is set to NUCLEOTIDE_SEQUENCE, got {mode_name}.")

        def _validate_allele_frequencies(param_name, freqs):
            for i, inner in enumerate(freqs):
                if len(inner) != 4:
                    raise ValueError(
                        f"Each inner array in '{param_name}' must have exactly "
                        f"4 values (A, C, G, T frequencies), but entry {i} has "
                        f"{len(inner)}.")
                total = sum(inner)
                if abs(total - 1.0) > 1e-6:
                    raise ValueError(
                        f"Allele frequencies in '{param_name}' must sum to 1.0, "
                        f"but entry {i} sums to {total}.")

        if barcode_allele_frequencies_per_genome_location is not None:
            _validate_allele_frequencies(
                'barcode_allele_frequencies_per_genome_location',
                barcode_allele_frequencies_per_genome_location)
        if drug_resistant_allele_frequencies_per_genome_location is not None:
            _validate_allele_frequencies(
                'drug_resistant_allele_frequencies_per_genome_location',
                drug_resistant_allele_frequencies_per_genome_location)
        if hrp_allele_frequencies_per_genome_location is not None:
            _validate_allele_frequencies(
                'hrp_allele_frequencies_per_genome_location',
                hrp_allele_frequencies_per_genome_location)

        if barcode_string is not None:
            self._intervention.Barcode_String = barcode_string
        if drug_resistant_string is not None:
            self._intervention.Drug_Resistant_String = drug_resistant_string
        if hrp_string is not None:
            self._intervention.HRP_String = hrp_string
        if barcode_allele_frequencies_per_genome_location is not None:
            self._intervention.Barcode_Allele_Frequencies_Per_Genome_Location = barcode_allele_frequencies_per_genome_location
        if drug_resistant_allele_frequencies_per_genome_location is not None:
            self._intervention.Drug_Resistant_Allele_Frequencies_Per_Genome_Location = drug_resistant_allele_frequencies_per_genome_location
        if hrp_allele_frequencies_per_genome_location is not None:
            self._intervention.HRP_Allele_Frequencies_Per_Genome_Location = hrp_allele_frequencies_per_genome_location
        if msp_variant_value is not None:
            self._intervention.MSP_Variant_Value = msp_variant_value
        if pfemp1_variants_values is not None:
            self._intervention.PfEMP1_Variants_Values = pfemp1_variants_values

        # Set after other params to avoid s2c schema dependency resets
        self._intervention.Create_Nucleotide_Sequence_From = create_nucleotide_sequence_from


class OutbreakIndividualMalariaVarGenes(IndividualIntervention):
    """
    The **OutbreakIndividualMalariaVarGenes** intervention class creates an outbreak with specific
    var gene (PfEMP1) variant types for modeling antigenic variation. This intervention is
    part of the Full Parasite Genetics (FPG) model. See
    [Full Parasite Genetics (FPG) Model](https://emod.idmod.org/emodpy-malaria/emod/malaria-model-fpg/) for details.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        msp_type (int, optional):
            The Merozoite Surface Protein (MSP) variant value of the infection. This value
            determines how antibodies recognize merozoites during blood-stage infection and
            must be less than or equal to the ``Falciparum_MSP_Variants`` value set via
            ``malaria_config.set_parasite_genetics_params()``. Range: 0 to 1000.
            Default value: 0

        irbc_type (list[int], optional):
            The array of PfEMP1 major epitope variant values, which define how antibodies
            recognize infected red blood cells. Each value in the array must be less than
            or equal to the ``Falciparum_PfEMP1_Variants`` value set via
            ``malaria_config.set_parasite_genetics_params()``. The
            array must contain exactly 50 values. Range per value: 0 to 10000.
            Default value: None

        minor_epitope_type (list[int], optional):
            The array of PfEMP1 minor epitope variant values. The array must contain
            exactly 50 values. Each value must be less than or equal to
            Falciparum_Nonspecific_Types multiplied by 5
            (``MINOR_EPITOPE_VARS_PER_SET``). Range per value: 0 to 10000.
            Default value: None

        ignore_immunity (bool, optional):
            If True, individuals will be force-infected with the specified parasite strain
            regardless of their actual immunity level. Set to False to have immunity
            affect whether the infection takes hold.
            Default value: True

        incubation_period_override (int, optional):
            The incubation period, in days, that infected individuals go through before
            becoming infectious. This overrides the incubation period set in the
            configuration file. Set to -1 to use the default incubation period from
            configuration settings. Range: -1 to 2147480000.
            Default value: -1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 msp_type: int = 0,
                 irbc_type: list[int] = None,
                 minor_epitope_type: list[int] = None,
                 ignore_immunity: bool = True,
                 incubation_period_override: int = -1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OutbreakIndividualMalariaVarGenes', common_intervention_parameters)
        campaign.implicits.append(partial(
            validate_malaria_model,
            intervention_name="OutbreakIndividualMalariaVarGenes"))

        self._intervention.MSP_Type = msp_type
        self._intervention.Ignore_Immunity = 1 if ignore_immunity else 0
        self._intervention.Incubation_Period_Override = incubation_period_override

        if irbc_type is not None:
            self._intervention.IRBC_Type = irbc_type
        if minor_epitope_type is not None:
            self._intervention.Minor_Epitope_Type = minor_epitope_type


# __all_exports: A list of classes that are intended to be exported from this module.
# the private classes are commented out until we have time to review and test them.
__all_exports = [
    AntimalarialDrug,
    AdherentDrug,
    MultiPackComboDrug,
    MalariaDiagnostic,
    SimpleBednet,
    UsageDependentBednet,
    MultiInsecticideUsageDependentBednet,
    IRSHousingModification,
    MultiInsecticideIRSHousingModification,
    ScreeningHousingModification,
    SpatialRepellentHousingModification,
    SimpleIndividualRepellent,
    IndoorIndividualEmanator,
    HumanHostSeekingTrap,
    Ivermectin,
    # _RTSSVaccine intentionally excluded — not part of public API
    BitingRisk,
    SimpleHealthSeekingBehavior,
    OutbreakIndividualMalariaGenetics,
    OutbreakIndividualMalariaVarGenes,
    FemaleContraceptive,
    IVCalendar,
    BroadcastEvent,
    BroadcastEventToOtherNodes,
    ControlledVaccine,
    DelayedIntervention,
    IndividualImmunityChanger,
    IndividualNonDiseaseDeathRateModifier,
    MigrateIndividuals,
    MultiEffectBoosterVaccine,
    MultiEffectVaccine,
    MultiInterventionDistributor,
    OutbreakIndividual,
    PropertyValueChanger,
    SimpleBoosterVaccine,
    SimpleVaccine,
    StandardDiagnostic,
]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
