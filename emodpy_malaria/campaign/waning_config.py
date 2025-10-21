from emodpy.campaign.waning_config import AbstractWaningConfig, BaseWaningConfig, Constant, MapLinear, MapPiecewise, RandomBox, \
    MapLinearAge, MapLinearSeasonal, Box, BoxExponential, Exponential, Combo


# __all_exports: A list of classes that are intended to be exported from this module.
# These classes include the BaseWaningConfig, Constant, MapLinear, MapPiecewise, RandomBox, MapLinearAge,
# MapLinearSeasonal, Box, BoxExponential, Exponential, and Combo classes.

__all_exports = [
    AbstractWaningConfig,
    BaseWaningConfig,
    Constant,
    MapLinear,
    MapPiecewise,
    RandomBox,
    MapLinearAge,
    MapLinearSeasonal,
    Box,
    BoxExponential,
    Exponential,
    Combo]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.
# During the documentation build with Sphinx, these classes will be displayed as belonging to the 'emodpy_malaria' package,
# not the 'emodpy' package.
# For example, the 'MapLinear' class will be documented as 'emodpy_malaria.campaign.waning_config.MapLinear(...)'.
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
