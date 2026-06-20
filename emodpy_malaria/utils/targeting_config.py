from emodpy.utils.targeting_config import AbstractTargetingConfig, BaseTargetingConfig
from emodpy.utils.targeting_config import HasIP, HasIntervention
from emodpy.utils.targeting_config import IsPregnant as _IsPregnantBase


def _validate_birth_rate_dependence(config):
    brd = config.parameters.Birth_Rate_Dependence
    valid = ("INDIVIDUAL_PREGNANCIES", "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR")
    if brd not in valid:
        raise ValueError(
            f"Config parameter 'Birth_Rate_Dependence' is set to '{brd}' but "
            f"IsPregnant targeting requires '{valid[0]}' or '{valid[1]}'.")
    return config


class IsPregnant(_IsPregnantBase):
    """
    Select the individual based on whether or not they are pregnant.

    Registers a validation implicit that checks **Birth_Rate_Dependence** is set to
    ``INDIVIDUAL_PREGNANCIES`` or ``INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR``.
    """

    def to_schema_dict(self, campaign):
        campaign.implicits.append(_validate_birth_rate_dependence)
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
