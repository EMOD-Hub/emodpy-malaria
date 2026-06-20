from emod_api import schema_to_class as s2c

from emodpy.campaign.waning_config import AbstractWaningConfig, BaseWaningConfig, Constant, MapLinear, MapPiecewise, \
    RandomBox, MapLinearAge, MapLinearSeasonal, Box, BoxExponential, Exponential, Combo


class InsecticideWaningEffect_K:
    """
    Defines insecticide killing efficacy for use in multi-insecticide interventions. Each instance
    pairs an insecticide name with a killing waning effect configuration.

    Used by:

    * :class:`~emodpy_malaria.campaign.node_intervention.MultiInsecticideIndoorSpaceSpraying`
    * :class:`~emodpy_malaria.campaign.node_intervention.MultiInsecticideSpaceSpraying`

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The waning effect configuration for insecticidal killing efficacy. Specify how this
            effect decays over time using one of the waning effect classes in
            :mod:`emodpy_malaria.campaign.waning_config`.

        insecticide_name (str, optional):
            The name of the insecticide defined in the **Insecticides** configuration parameter.
            If insecticides are being used, this must match one of those values. It cannot have
            a value if you did not configure the **Insecticides** parameter. See
            `vector-model-insecticide-resistance <vector-model-insecticide-resistance.html>`_
            and `vector-model-genetics <vector-model-genetics.html>`_ for details.
            Default value: None
    """

    def __init__(self, campaign, killing_config: AbstractWaningConfig, insecticide_name: str = None):
        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(
                f"'killing_config' must be an AbstractWaningConfig instance, "
                f"got {type(killing_config).__name__}.")
        self._campaign = campaign
        self._killing_config = killing_config
        self._insecticide_name = insecticide_name

    def to_schema_dict(self) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults(
            "idmType:InsecticideWaningEffect_K", schema_json=self._campaign.get_schema())
        obj.Killing_Config = self._killing_config.to_schema_dict(self._campaign)
        if self._insecticide_name is not None:
            obj.Insecticide_Name = self._insecticide_name
        obj.pop("schema", None)
        obj.pop("explicits", None)
        return obj


class InsecticideWaningEffect_RK:
    """
    Defines insecticide repelling and killing efficacy for use in multi-insecticide interventions.
    Each instance pairs an insecticide name with repelling and killing waning effect configurations.
    A vector is repelled before any killing can occur. Repelled vectors survive and do not
    attempt to feed again until the following day.

    Used by:

    * :class:`~emodpy_malaria.campaign.individual_intervention.MultiInsecticideIRSHousingModification`

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The waning effect configuration for insecticidal killing efficacy. Killing
            probabilities are applied to vectors that were not repelled. Specify how this
            effect decays over time using one of the waning effect classes in
            :mod:`emodpy_malaria.campaign.waning_config`.

        repelling_config (AbstractWaningConfig, required):
            The waning effect configuration for repelling efficacy. A vector is repelled
            before any killing can occur. Repelled vectors survive and do not attempt to
            feed again until the following day. Specify how this effect decays over time
            using one of the waning effect classes in
            :mod:`emodpy_malaria.campaign.waning_config`.

        insecticide_name (str, optional):
            The name of the insecticide defined in the **Insecticides** configuration parameter.
            If insecticides are being used, this must match one of those values. It cannot have
            a value if you did not configure the **Insecticides** parameter. See
            `vector-model-insecticide-resistance <vector-model-insecticide-resistance.html>`_
            and `vector-model-genetics <vector-model-genetics.html>`_ for details.
            Default value: None
    """

    def __init__(self, campaign, killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig, insecticide_name: str = None):
        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(
                f"'killing_config' must be an AbstractWaningConfig instance, "
                f"got {type(killing_config).__name__}.")
        if not isinstance(repelling_config, AbstractWaningConfig):
            raise ValueError(
                f"'repelling_config' must be an AbstractWaningConfig instance, "
                f"got {type(repelling_config).__name__}.")
        self._campaign = campaign
        self._killing_config = killing_config
        self._repelling_config = repelling_config
        self._insecticide_name = insecticide_name

    def to_schema_dict(self) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults(
            "idmType:InsecticideWaningEffect_RK", schema_json=self._campaign.get_schema())
        obj.Killing_Config = self._killing_config.to_schema_dict(self._campaign)
        obj.Repelling_Config = self._repelling_config.to_schema_dict(self._campaign)
        if self._insecticide_name is not None:
            obj.Insecticide_Name = self._insecticide_name
        obj.pop("schema", None)
        obj.pop("explicits", None)
        return obj


class InsecticideWaningEffect_RBK:
    """
    Defines insecticide repelling, blocking, and killing efficacy for use in multi-insecticide
    interventions. Each instance pairs an insecticide name with repelling, blocking, and killing
    waning effect configurations. A vector is repelled before any blocking or killing can occur;
    repelled vectors survive and do not attempt to feed again until the following day. A vector
    must be blocked before it can be killed.

    Used by:

    * :class:`~emodpy_malaria.campaign.individual_intervention.MultiInsecticideUsageDependentBednet`

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The waning effect configuration for insecticidal killing efficacy. For a
            meal-seeking vector to be affected, it must be successfully blocked first,
            mimicking the mosquito landing on the bednet. Killing probabilities are applied
            to the subset of mosquitoes that are blocked. Specify how this effect decays
            over time using one of the waning effect classes in
            :mod:`emodpy_malaria.campaign.waning_config`.

        blocking_config (AbstractWaningConfig, required):
            The waning effect configuration for blocking efficacy. Blocking probabilities
            are applied to the subset of meal-seeking mosquitoes that have not been
            repelled. Specify how this effect decays over time using one of the waning
            effect classes in :mod:`emodpy_malaria.campaign.waning_config`.

        repelling_config (AbstractWaningConfig, required):
            The waning effect configuration for repelling efficacy. This is the first
            effect applied to meal-seeking mosquitoes that encounter the net. Repelled
            vectors survive and do not attempt to feed again until the following day and
            are not affected by the blocking or killing effects. Specify how this effect
            decays over time using one of the waning effect classes in
            :mod:`emodpy_malaria.campaign.waning_config`.

        insecticide_name (str, optional):
            The name of the insecticide defined in the **Insecticides** configuration parameter.
            If insecticides are being used, this must match one of those values. It cannot have
            a value if you did not configure the **Insecticides** parameter. See
            `vector-model-insecticide-resistance <vector-model-insecticide-resistance.html>`_
            and `vector-model-genetics <vector-model-genetics.html>`_ for details.
            Default value: None
    """

    def __init__(self, campaign, killing_config: AbstractWaningConfig,
                 blocking_config: AbstractWaningConfig, repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None):
        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(
                f"'killing_config' must be an AbstractWaningConfig instance, "
                f"got {type(killing_config).__name__}.")
        if not isinstance(blocking_config, AbstractWaningConfig):
            raise ValueError(
                f"'blocking_config' must be an AbstractWaningConfig instance, "
                f"got {type(blocking_config).__name__}.")
        if not isinstance(repelling_config, AbstractWaningConfig):
            raise ValueError(
                f"'repelling_config' must be an AbstractWaningConfig instance, "
                f"got {type(repelling_config).__name__}.")
        self._campaign = campaign
        self._killing_config = killing_config
        self._blocking_config = blocking_config
        self._repelling_config = repelling_config
        self._insecticide_name = insecticide_name

    def to_schema_dict(self) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults(
            "idmType:InsecticideWaningEffect_RBK", schema_json=self._campaign.get_schema())
        obj.Killing_Config = self._killing_config.to_schema_dict(self._campaign)
        obj.Blocking_Config = self._blocking_config.to_schema_dict(self._campaign)
        obj.Repelling_Config = self._repelling_config.to_schema_dict(self._campaign)
        if self._insecticide_name is not None:
            obj.Insecticide_Name = self._insecticide_name
        obj.pop("schema", None)
        obj.pop("explicits", None)
        return obj


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
    Combo,
    InsecticideWaningEffect_K,
    InsecticideWaningEffect_RK,
    InsecticideWaningEffect_RBK]

for _ in __all_exports:
    _.__module__ = __name__

__all__ = [_.__name__ for _ in __all_exports]
