from emod_api import campaign as api_campaign, schema_to_class as s2c

from emodpy.campaign.base_intervention import IndividualIntervention, NodeIntervention
from emodpy.campaign.event_coordinator import InterventionDistributorEventCoordinator
from emodpy_malaria.campaign.common import TargetDemographicsConfig, ValueMap, PropertyRestrictions
from emodpy_malaria.utils.targeting_config import AbstractTargetingConfig

from typing import Union

# ported from emodpy/campaign/event_coordinator.py
# The StandardEventCoordinator coordinator class distributes an individual-level or node-level intervention to
# a specified fraction of individuals or nodes within a node set.
from emodpy.campaign.event_coordinator import StandardEventCoordinator


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [StandardEventCoordinator]

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
