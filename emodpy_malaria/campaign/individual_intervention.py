import emod_api.schema_to_class as s2c

from emodpy.utils import validate_key_value_pair
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
from emodpy.utils import validate_value_range
from emodpy.campaign.utils import set_event
from emodpy_malaria.utils.emod_enum import (SensitivityType, SettingType, RelationshipType, EventOrConfig, PrioritizePartnersBy,
                                        CondomUsageParametersType)
from emodpy_malaria.utils.distributions import BaseDistribution
from emodpy_malaria.campaign.common import ValueMap, CommonInterventionParameters
from emodpy_malaria.campaign.waning_config import AbstractWaningConfig
from emod_api import campaign as api_campaign

from typing import Union


class Ivermectin(IndividualIntervention):
    """
        Configures Ivermectin intervention.

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        killing_waning_config: The waning configuration for the killing effect of Ivermectin.
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        common_intervention_parameters: The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.


    """
    def __init__(self,
                 campaign: api_campaign,
                 killing_waning_config: AbstractWaningConfig,
                 insecticide: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'Ivermectin', common_intervention_parameters)
        if not isinstance(killing_waning_config, AbstractWaningConfig):
            raise ValueError(f"killing_waning_config must be an instance of AbstractWaningConfig, not {type(killing_waning_config)}.")
        self._intervention.Killing_Config = killing_waning_config.to_schema_dict(campaign)
        if insecticide is not None:
            self._intervention.Insecticide_Name = insecticide  # add validate insecticide? do we have access to config here?


# __all_exports: A list of classes that are intended to be exported from this module.
# the private classes are commented out until we have time to review and test them.
__all_exports = [
    Ivermectin,
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
