from emodpy.utils.emod_enum import StrEnum, DistributionType, NodeSelectionType, VaccineType, SensitivityType, \
    EventOrConfig, SettingType, ThresholdType, EventType, BirthRateDependence  # noqa: F401


class DiagnosticType(StrEnum):
    BLOOD_SMEAR_PARASITES = "BLOOD_SMEAR_PARASITES"
    BLOOD_SMEAR_GAMETOCYTES = "BLOOD_SMEAR_GAMETOCYTES"
    PCR_PARASITES = "PCR_PARASITES"
    PCR_GAMETOCYTES = "PCR_GAMETOCYTES"
    PF_HRP2 = "PF_HRP2"
    TRUE_PARASITE_DENSITY = "TRUE_PARASITE_DENSITY"
    FEVER = "FEVER"


class HabitatType(StrEnum):
    # NONE = "NONE"  # internal use only — not a valid user-facing habitat type
    ALL_HABITATS = "ALL_HABITATS"
    TEMPORARY_RAINFALL = "TEMPORARY_RAINFALL"
    WATER_VEGETATION = "WATER_VEGETATION"
    HUMAN_POPULATION = "HUMAN_POPULATION"
    CONSTANT = "CONSTANT"
    BRACKISH_SWAMP = "BRACKISH_SWAMP"
    LINEAR_SPLINE = "LINEAR_SPLINE"


class VectorGender(StrEnum):
    VECTOR_FEMALE = "VECTOR_FEMALE"
    VECTOR_MALE = "VECTOR_MALE"
    VECTOR_BOTH_GENDERS = "VECTOR_BOTH_GENDERS"


class VectorGeneticsStratification(StrEnum):
    GENOME = "GENOME"
    ALLELE = "ALLELE"
    ALLELE_FREQ = "ALLELE_FREQ"
    SPECIFIC_GENOME = "SPECIFIC_GENOME"


class MalariaStrainModel(StrEnum):
    FALCIPARUM_NONRANDOM_STRAIN = "FALCIPARUM_NONRANDOM_STRAIN"
    FALCIPARUM_RANDOM50_STRAIN = "FALCIPARUM_RANDOM50_STRAIN"
    FALCIPARUM_RANDOM_STRAIN = "FALCIPARUM_RANDOM_STRAIN"
    FALCIPARUM_FIXED_STRAIN = "FALCIPARUM_FIXED_STRAIN"
    FALCIPARUM_STRAIN_GENERATOR = "FALCIPARUM_STRAIN_GENERATOR"


class EIRType(StrEnum):
    MONTHLY = "MONTHLY"
    DAILY = "DAILY"


class InputEIRAgeDependence(StrEnum):
    OFF = "OFF"
    LINEAR = "LINEAR"
    SURFACE_AREA_DEPENDENT = "SURFACE_AREA_DEPENDENT"


class NonAdherenceOption(StrEnum):
    NEXT_UPDATE = "NEXT_UPDATE"
    NEXT_DOSAGE_TIME = "NEXT_DOSAGE_TIME"
    LOST_TAKE_NEXT = "LOST_TAKE_NEXT"
    STOP = "STOP"


class NucleotideSequenceOrigin(StrEnum):
    BARCODE_STRING = "BARCODE_STRING"
    ALLELE_FREQUENCIES = "ALLELE_FREQUENCIES"
    NUCLEOTIDE_SEQUENCE = "NUCLEOTIDE_SEQUENCE"


class ChallengeType(StrEnum):
    INFECTIOUS_BITES = "InfectiousBites"
    SPOROZOITES = "Sporozoites"


class MosquitoReleaseType(StrEnum):
    FIXED_NUMBER = "FIXED_NUMBER"
    RATIO = "RATIO"


class ArtificialDietTarget(StrEnum):
    AD_WITHIN_VILLAGE = "AD_WithinVillage"
    AD_OUTSIDE_VILLAGE = "AD_OutsideVillage"


class VectorCountType(StrEnum):
    ALLELE_FREQ = "ALLELE_FREQ"
    GENOME_FRACTION = "GENOME_FRACTION"


class WolbachiaType(StrEnum):
    VECTOR_WOLBACHIA_FREE = "VECTOR_WOLBACHIA_FREE"
    VECTOR_WOLBACHIA_A = "VECTOR_WOLBACHIA_A"
    VECTOR_WOLBACHIA_B = "VECTOR_WOLBACHIA_B"
    VECTOR_WOLBACHIA_AB = "VECTOR_WOLBACHIA_AB"


class VarGeneRandomnessType(StrEnum):
    ALL_RANDOM = "ALL_RANDOM"
    FIXED_NEIGHBORHOOD = "FIXED_NEIGHBORHOOD"
    FIXED_MSP = "FIXED_MSP"


class DriverType(StrEnum):
    CLASSIC = "CLASSIC"
    INTEGRAL_AUTONOMOUS = "INTEGRAL_AUTONOMOUS"
    X_SHRED = "X_SHRED"
    Y_SHRED = "Y_SHRED"
    DAISY_CHAIN = "DAISY_CHAIN"


class VectorTrait(StrEnum):
    INFECTED_BY_HUMAN = "INFECTED_BY_HUMAN"
    FECUNDITY = "FECUNDITY"
    FEMALE_EGG_RATIO = "FEMALE_EGG_RATIO"
    STERILITY = "STERILITY"
    TRANSMISSION_TO_HUMAN = "TRANSMISSION_TO_HUMAN"
    ADJUST_FERTILE_EGGS = "ADJUST_FERTILE_EGGS"
    MORTALITY = "MORTALITY"
    INFECTED_PROGRESS = "INFECTED_PROGRESS"
    OOCYST_PROGRESSION = "OOCYST_PROGRESSION"
    SPOROZOITE_MORTALITY = "SPOROZOITE_MORTALITY"


class PKPDModel(StrEnum):
    FIXED_DURATION_CONSTANT_EFFECT = "FIXED_DURATION_CONSTANT_EFFECT"
    CONCENTRATION_VERSUS_TIME = "CONCENTRATION_VERSUS_TIME"


class ParasiteSwitchType(StrEnum):
    CONSTANT_SWITCH_RATE_2VARS = "CONSTANT_SWITCH_RATE_2VARS"
    RATE_PER_PARASITE_7VARS = "RATE_PER_PARASITE_7VARS"
    RATE_PER_PARASITE_5VARS_DECAYING = "RATE_PER_PARASITE_5VARS_DECAYING"


class VectorSamplingType(StrEnum):
    TRACK_ALL_VECTORS = "TRACK_ALL_VECTORS"
    SAMPLE_IND_VECTORS = "SAMPLE_IND_VECTORS"
    VECTOR_COMPARTMENTS_NUMBER = "VECTOR_COMPARTMENTS_NUMBER"
    VECTOR_COMPARTMENTS_PERCENT = "VECTOR_COMPARTMENTS_PERCENT"


class EggHatchDensityDependence(StrEnum):
    NO_DENSITY_DEPENDENCE = "NO_DENSITY_DEPENDENCE"
    DENSITY_DEPENDENCE = "DENSITY_DEPENDENCE"


class EggSaturationAtOviposition(StrEnum):
    NO_SATURATION = "NO_SATURATION"
    SATURATION_AT_OVIPOSITION = "SATURATION_AT_OVIPOSITION"
    SIGMOIDAL_SATURATION = "SIGMOIDAL_SATURATION"


class InnateImmuneVariationType(StrEnum):
    NONE = "NONE"
    PYROGENIC_THRESHOLD = "PYROGENIC_THRESHOLD"
    CYTOKINE_KILLING = "CYTOKINE_KILLING"
    PYROGENIC_THRESHOLD_VS_AGE_CONCAVE = "PYROGENIC_THRESHOLD_VS_AGE_CONCAVE"
    PYROGENIC_THRESHOLD_VS_AGE_INCREASING_AND_CYTOKINE_KILLING_INVERSE = "PYROGENIC_THRESHOLD_VS_AGE_INCREASING_AND_CYTOKINE_KILLING_INVERSE"


class ClimateModel(StrEnum):
    CLIMATE_OFF = "CLIMATE_OFF"
    CLIMATE_CONSTANT = "CLIMATE_CONSTANT"
    CLIMATE_KOPPEN = "CLIMATE_KOPPEN"
    CLIMATE_BY_DATA = "CLIMATE_BY_DATA"


class ClimateUpdateResolution(StrEnum):
    CLIMATE_UPDATE_YEAR = "CLIMATE_UPDATE_YEAR"
    CLIMATE_UPDATE_MONTH = "CLIMATE_UPDATE_MONTH"
    CLIMATE_UPDATE_WEEK = "CLIMATE_UPDATE_WEEK"
    CLIMATE_UPDATE_DAY = "CLIMATE_UPDATE_DAY"
    CLIMATE_UPDATE_HOUR = "CLIMATE_UPDATE_HOUR"


class PopulationScaleType(StrEnum):
    USE_INPUT_FILE = "USE_INPUT_FILE"
    FIXED_SCALING = "FIXED_SCALING"


class AgeDependentBitingRiskType(StrEnum):
    OFF = "OFF"
    LINEAR = "LINEAR"
    SURFACE_AREA_DEPENDENT = "SURFACE_AREA_DEPENDENT"


class SpatialOutputChannel(StrEnum):
    POPULATION = "Population"
    PREVALENCE = "Prevalence"
    TRUE_PREVALENCE = "True_Prevalence"
    NEW_INFECTIONS = "New_Infections"
    NEW_CLINICAL_CASES = "New_Clinical_Cases"
    NEW_SEVERE_CASES = "New_Severe_Cases"
    NEW_REPORTED_INFECTIONS = "New_Reported_Infections"
    INFECTED = "Infected"
    DISEASE_DEATHS = "Disease_Deaths"
    BIRTHS = "Births"
    CAMPAIGN_COST = "Campaign_Cost"
    ADULT_VECTORS = "Adult_Vectors"
    INFECTIOUS_VECTORS = "Infectious_Vectors"
    DAILY_EIR = "Daily_EIR"
    DAILY_BITES_PER_HUMAN = "Daily_Bites_Per_Human"
    HUMAN_INFECTIOUS_RESERVOIR = "Human_Infectious_Reservoir"
    MEAN_PARASITEMIA = "Mean_Parasitemia"
    FEVER_PREVALENCE = "Fever_Prevalence"
    BLOOD_SMEAR_PARASITE_PREVALENCE = "Blood_Smear_Parasite_Prevalence"
    BLOOD_SMEAR_GAMETOCYTE_PREVALENCE = "Blood_Smear_Gametocyte_Prevalence"
    PCR_PARASITE_PREVALENCE = "PCR_Parasite_Prevalence"
    PCR_GAMETOCYTE_PREVALENCE = "PCR_Gametocyte_Prevalence"
    PF_HRP2_PREVALENCE = "PfHRP2_Prevalence"
    NEW_DIAGNOSTIC_PREVALENCE = "New_Diagnostic_Prevalence"
    AIR_TEMPERATURE = "Air_Temperature"
    LAND_TEMPERATURE = "Land_Temperature"
    RAINFALL = "Rainfall"
    RELATIVE_HUMIDITY = "Relative_Humidity"


class VectorStateEnum(StrEnum):
    STATE_INFECTIOUS = "STATE_INFECTIOUS"
    STATE_INFECTED = "STATE_INFECTED"
    STATE_ADULT = "STATE_ADULT"
    STATE_MALE = "STATE_MALE"
    STATE_IMMATURE = "STATE_IMMATURE"
    STATE_LARVA = "STATE_LARVA"
    STATE_EGG = "STATE_EGG"


class DrugResistantStatisticType(StrEnum):
    NUM_PEOPLE_WITH_RESISTANT_INFECTION = "NUM_PEOPLE_WITH_RESISTANT_INFECTION"
    NUM_INFECTIONS = "NUM_INFECTIONS"


class ModifierEquationType(StrEnum):
    EXPONENTIAL = "EXPONENTIAL"
    LINEAR = "LINEAR"


__all_exports = [
    StrEnum,
    DistributionType,
    NodeSelectionType,
    VaccineType,
    SensitivityType,
    EventOrConfig,
    SettingType,
    ThresholdType,
    EventType,
    BirthRateDependence,
    DiagnosticType,
    HabitatType,
    VectorGender,
    VectorGeneticsStratification,
    MalariaStrainModel,
    EIRType,
    InputEIRAgeDependence,
    NonAdherenceOption,
    NucleotideSequenceOrigin,
    ChallengeType,
    MosquitoReleaseType,
    ArtificialDietTarget,
    VectorCountType,
    WolbachiaType,
    VarGeneRandomnessType,
    DriverType,
    VectorTrait,
    PKPDModel,
    ParasiteSwitchType,
    VectorSamplingType,
    EggHatchDensityDependence,
    EggSaturationAtOviposition,
    InnateImmuneVariationType,
    ClimateModel,
    ClimateUpdateResolution,
    PopulationScaleType,
    AgeDependentBitingRiskType,
    SpatialOutputChannel,
    VectorStateEnum,
    DrugResistantStatisticType,
    ModifierEquationType,
]

for _ in __all_exports:
    _.__module__ = __name__

__all__ = [_.__name__ for _ in __all_exports]
