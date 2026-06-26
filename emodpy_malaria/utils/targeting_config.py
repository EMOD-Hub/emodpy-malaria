from emodpy.utils.targeting_config import AbstractTargetingConfig, BaseTargetingConfig
from emodpy.utils.targeting_config import HasIP, HasIntervention
from emodpy.utils.targeting_config import IsPregnant as _IsPregnantBase
from emodpy_malaria.utils.config_utils import validate_birth_rate_dependence


class IsPregnant(_IsPregnantBase):
    """
    Select the individual based on whether or not they are pregnant.

    Registers a validation implicit that checks **Birth_Rate_Dependence** is set to
    ``INDIVIDUAL_PREGNANCIES`` or ``INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR``.
    """

    def to_schema_dict(self, campaign):
        campaign.implicits.append(validate_birth_rate_dependence)
        return super().to_schema_dict(campaign)


__all_exports = [
    AbstractTargetingConfig,
    BaseTargetingConfig,
    HasIP,
    HasIntervention,
    IsPregnant,
]

for _ in __all_exports:
    _.__module__ = __name__

__all__ = [_.__name__ for _ in __all_exports]
