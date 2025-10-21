# ported from: emodpy/campaign/node_intervention.py
# These are the node-level intervention classes that are available in this package, please import them from this module.
from emodpy.campaign.node_intervention import MultiNodeInterventionDistributor
from emodpy.campaign.node_intervention import BroadcastNodeEvent
from emodpy.campaign.node_intervention import ImportPressure
from emodpy.campaign.node_intervention import MigrateFamily
from emodpy.campaign.node_intervention import NodePropertyValueChanger
from emodpy.campaign.node_intervention import Outbreak


# __all_exports: A list of classes that are intended to be exported from this module.
# the private classes are commented out until we have time to review and test them.
__all_exports = [
    MultiNodeInterventionDistributor,
    BroadcastNodeEvent,
    ImportPressure,
    MigrateFamily,
    NodePropertyValueChanger,
    Outbreak
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
