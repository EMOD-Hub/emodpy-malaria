"""MalariaNode: malaria-aware extension of emod-api's Node."""

from __future__ import annotations

import warnings
from typing import Callable, List, Tuple

from emod_api.demographics.node import Node


def _set_enable_demog_risk(config):
    config.parameters.Enable_Demographics_Risk = 1
    return config


def _set_innate_immune_variation_type(config, variation_type: str):
    config.parameters.Innate_Immune_Variation_Type = variation_type
    return config


class MalariaNode(Node):
    """Node subclass that supports malaria-specific demographics distributions.

    Adds risk and innate-immune distribution storage, serialization, and
    deserialization.  These distributions are simple-only (flag + value1 +
    value2) and are written into the ``IndividualAttributes`` section of
    the demographics JSON.
    """

    def _set_risk_simple_distribution(self, flag: int, value1: float, value2: float):
        """Set a simple risk distribution on this node's individual attributes.

        Args:
            flag (int): Simple distribution flag (determines distribution type).
            value1 (float): Distribution parameter 1.
            value2 (float): Distribution parameter 2.
        """
        self.individual_attributes.risk_distribution_flag = flag
        self.individual_attributes.risk_distribution1 = value1
        self.individual_attributes.risk_distribution2 = value2

    def _set_innate_immune_simple_distribution(self, flag: int, value1: float, value2: float):
        """Set a simple innate immune distribution on this node's individual attributes.

        Args:
            flag (int): Simple distribution flag (determines distribution type).
            value1 (float): Distribution parameter 1.
            value2 (float): Distribution parameter 2.
        """
        self.individual_attributes.innate_immune_distribution_flag = flag
        self.individual_attributes.innate_immune_distribution1 = value1
        self.individual_attributes.innate_immune_distribution2 = value2

    def to_dict(self) -> dict:
        d = super().to_dict()
        ia = d.get("IndividualAttributes", {})

        risk_flag = getattr(self.individual_attributes, "risk_distribution_flag", None)
        if risk_flag is not None:
            ia["RiskDistributionFlag"] = risk_flag
            ia["RiskDistribution1"] = self.individual_attributes.risk_distribution1
            ia["RiskDistribution2"] = self.individual_attributes.risk_distribution2 if self.individual_attributes.risk_distribution2 is not None else 0
            d["IndividualAttributes"] = ia

        innate_flag = getattr(self.individual_attributes, "innate_immune_distribution_flag", None)
        if innate_flag is not None:
            ia["InnateImmuneDistributionFlag"] = innate_flag
            ia["InnateImmuneDistribution1"] = self.individual_attributes.innate_immune_distribution1
            ia["InnateImmuneDistribution2"] = self.individual_attributes.innate_immune_distribution2 if self.individual_attributes.innate_immune_distribution2 is not None else 0
            d["IndividualAttributes"] = ia

        return d

    @classmethod
    def from_data(cls, data: dict) -> Tuple["MalariaNode", List[Callable]]:
        node, implicit_functions = super().from_data(data)
        ia_dict = data.get("IndividualAttributes") or {}

        risk_flag = ia_dict.get("RiskDistributionFlag")
        if risk_flag is not None:
            node.individual_attributes.risk_distribution_flag = risk_flag
            node.individual_attributes.risk_distribution1 = ia_dict.get("RiskDistribution1")
            node.individual_attributes.risk_distribution2 = ia_dict.get("RiskDistribution2")
            implicit_functions.append(_set_enable_demog_risk)

        innate_flag = ia_dict.get("InnateImmuneDistributionFlag")
        if innate_flag is not None:
            node.individual_attributes.innate_immune_distribution_flag = innate_flag
            node.individual_attributes.innate_immune_distribution1 = ia_dict.get("InnateImmuneDistribution1")
            node.individual_attributes.innate_immune_distribution2 = ia_dict.get("InnateImmuneDistribution2")
            warnings.warn(
                "InnateImmuneDistribution loaded from file. Pyrogenic vs. cytokine-killing vs. NONE "
                "is unknown. Config may need updating to ensure Innate_Immune_Variation_Type is set properly.",
                Warning,
                stacklevel=2,
            )

        return node, implicit_functions
