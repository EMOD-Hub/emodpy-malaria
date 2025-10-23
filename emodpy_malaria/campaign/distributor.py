from emod_api import campaign as api_campaign
from emodpy.campaign.base_intervention import IndividualIntervention
from emodpy.campaign.event import create_campaign_event

from emodpy_malaria.campaign.common import (TargetDemographicsConfig, PropertyRestrictions,
                                        ValueMap, CommonInterventionParameters as CIP)
from emodpy_malaria.utils.emod_enum import TargetDiseaseState
from emodpy_malaria.utils.targeting_config import AbstractTargetingConfig, HasIntervention

import pandas as pd
import warnings

# ported from emodpy/campaign/distributor.py

# This function adds the intervention(s) to the campaign at scheduled time with the given parameters.
# The start_year parameter is only allowed to be used in HIV, and it is recommended that HIV modelers use it to schedule
# the intervention(s) at the specified year instead of start_day.
from emodpy.campaign.distributor import add_intervention_scheduled

# This function configures the campaign to distribute an intervention to an individual when that individual broadcasts
# an event.
# The start_year parameter is only allowed to be used in HIV, and it is recommended that HIV modelers use it to define
# the specified year when the simulation starts to listen to the event instead of start_day.
from emodpy.campaign.distributor import add_intervention_triggered



# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [add_intervention_scheduled, add_intervention_triggered]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.
# During the documentation build with Sphinx, these classes will be displayed as belonging to the 'emodpy_malaria' package,
# not the 'emodpy' package.
# For example, the 'PropertyRestrictions' class will be documented as 'emodpy_malaria.campaign.common.PropertyRestrictions(...)'.
# This is crucial for accurately representing the source of these classes in the documentation.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
