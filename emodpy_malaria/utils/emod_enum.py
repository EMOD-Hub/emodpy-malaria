from emodpy.utils.emod_enum import StrEnum, DistributionType, NodeSelectionType, VaccineType, SensitivityType, \
    EventOrConfig, SettingType


class PrioritizePartnersBy(StrEnum):
    NO_PRIORITIZATION = 'NO_PRIORITIZATION'
    CHOSEN_AT_RANDOM = 'CHOSEN_AT_RANDOM'
    LONGER_TIME_IN_RELATIONSHIP = 'LONGER_TIME_IN_RELATIONSHIP'
    SHORTER_TIME_IN_RELATIONSHIP = 'SHORTER_TIME_IN_RELATIONSHIP'
    OLDER_AGE = 'OLDER_AGE'
    YOUNGER_AGE = 'YOUNGER_AGE'
    RELATIONSHIP_TYPE = 'RELATIONSHIP_TYPE'


class RelationshipType(StrEnum):
    TRANSITORY = 'TRANSITORY'
    INFORMAL = 'INFORMAL'
    MARITAL = 'MARITAL'
    COMMERCIAL = 'COMMERCIAL'
    COUNT = 'COUNT'


class CondomUsageParametersType(StrEnum):
    USE_DEFAULT = 'USE_DEFAULT'
    SPECIFY_USAGE = 'SPECIFY_USAGE'


class TargetDiseaseState(StrEnum):
    HIV_POSITIVE = 'HIV_Positive'
    HIV_NEGATIVE = 'HIV_Negative'
    TESTED_POSITIVE = 'Tested_Positive'
    TESTED_NEGATIVE = 'Tested_Negative'
    MALE_CIRCUMCISION_POSITIVE = 'Male_Circumcision_Positive'
    MALE_CIRCUMCISION_NEGATIVE = 'Male_Circumcision_Negative'
    HAS_INTERVENTION = 'Has_Intervention'
    NOT_HAVE_INTERVENTION = 'Not_Have_Intervention'


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [
    StrEnum,
    DistributionType,
    NodeSelectionType,
    VaccineType,
    SensitivityType,
    EventOrConfig,
    SettingType,
    PrioritizePartnersBy,
    RelationshipType,
    CondomUsageParametersType,
    TargetDiseaseState]


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
