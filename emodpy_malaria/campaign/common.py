from emod_api import campaign as api_campaign
from emod_api import schema_to_class as s2c
from emodpy_malaria.utils.emod_enum import TargetDiseaseState

from typing import Union

# Importing necessary classes from the emodpy.campaign.common module so user can import them from the current
# module: emodpy_malaria.campaign.common module
# These classes are essential for defining campaign configurations and properties in the EMOD model.

# CommonInterventionParameters: A class used to define common parameters for interventions.
from emodpy.campaign.common import CommonInterventionParameters as CommonInterventionParameters

# MAX_AGE_YEARS: A constant representing the maximum age in years considered in the model.
from emodpy.campaign.common import MAX_AGE_YEARS as EMODPY_MAX_AGE_YEARS

# TargetGender: A class used to specify the gender of individuals targeted by an intervention.
from emodpy.campaign.common import TargetGender as TargetGender

# TargetDemographicsConfig: A class used to define the demographic characteristics of individuals targeted by an
# intervention.
from emodpy.campaign.common import TargetDemographicsConfig as TargetDemographicsConfig

# RepetitionConfig: A class used to configure the number of times an intervention event will occur.
from emodpy.campaign.common import RepetitionConfig as RepetitionConfig

# PropertyRestrictions: A class used to specify property restrictions for an intervention.
from emodpy.campaign.common import PropertyRestrictions as PropertyRestrictions

# ValueMap: A class used to map values over a defined range of time.
from emodpy.campaign.common import ValueMap as ValueMap

# Assigning the imported MAX_AGE_YEARS constant from emodpy to a local constant for use within this module.
MAX_AGE_YEARS = EMODPY_MAX_AGE_YEARS


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [CommonInterventionParameters, PropertyRestrictions, TargetGender, TargetDemographicsConfig,
                 RepetitionConfig, ValueMap]

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
