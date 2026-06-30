from emodpy.campaign.common import CommonInterventionParameters as CommonInterventionParameters  # noqa: F401
from emodpy.campaign.common import MAX_AGE_YEARS as EMODPY_MAX_AGE_YEARS
from emodpy.campaign.common import TargetGender as TargetGender  # noqa: F401
from emodpy.campaign.common import TargetDemographicsConfig as TargetDemographicsConfig  # noqa: F401
from emodpy.campaign.common import RepetitionConfig as RepetitionConfig  # noqa: F401
from emodpy.campaign.common import PropertyRestrictions as PropertyRestrictions  # noqa: F401
from emodpy.campaign.common import ValueMap as ValueMap  # noqa: F401

MAX_AGE_YEARS = EMODPY_MAX_AGE_YEARS


__all_exports = [
    CommonInterventionParameters,
    TargetGender,
    TargetDemographicsConfig,
    RepetitionConfig,
    PropertyRestrictions,
    ValueMap,
]

for _ in __all_exports:
    _.__module__ = __name__

__all__ = [_.__name__ for _ in __all_exports] + ['MAX_AGE_YEARS']
