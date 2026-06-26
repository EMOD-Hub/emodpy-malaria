from emod_api import schema_to_class as s2c

from emodpy.campaign.waning_config import AbstractWaningConfig, BaseWaningConfig, Constant, MapLinear, MapPiecewise, \
    RandomBox, MapLinearAge, MapLinearSeasonal, Box, BoxExponential, Exponential, Combo


class InsecticideWaningEffect:
    """
    Defines insecticide waning effects for use in multi-insecticide interventions. Each
    instance pairs an insecticide name with one or more waning effect configurations for
    killing, repelling, and/or blocking.

    The class automatically determines the correct EMOD schema type based on which
    configs are provided:

    * **killing only** → used by
      [MultiInsecticideSpaceSpraying](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/node_intervention/)
      and
      [MultiInsecticideIndoorSpaceSpraying](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/node_intervention/)
    * **killing + repelling** → used by
      [MultiInsecticideIRSHousingModification](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/)
    * **killing + repelling + blocking** → used by
      [MultiInsecticideUsageDependentBednet](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/)

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The waning effect configuration for insecticidal killing efficacy. Specify how
            this effect decays over time using one of the waning effect classes in
            [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        repelling_config (AbstractWaningConfig, optional):
            The waning effect configuration for repelling efficacy. A vector is repelled
            before any blocking or killing can occur. Repelled vectors survive and do not
            attempt to feed again until the following day. Required for IRS and bednet
            multi-insecticide interventions.
            Default value: None

        blocking_config (AbstractWaningConfig, optional):
            The waning effect configuration for blocking efficacy. Blocking probabilities
            are applied to the subset of meal-seeking mosquitoes that have not been
            repelled. A vector must be blocked before it can be killed. Required for bednet
            multi-insecticide interventions. Cannot be provided without ``repelling_config``.
            Default value: None

        insecticide_name (str, optional):
            The name of the insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. If
            insecticides are being used, this must match one of those values. It cannot have
            a value if you did not configure insecticide resistance. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None
    """

    _VARIANT_SCHEMA = {
        "K": "idmType:InsecticideWaningEffect_K",
        "RK": "idmType:InsecticideWaningEffect_RK",
        "RBK": "idmType:InsecticideWaningEffect_RBK",
    }

    def __init__(self, campaign,
                 killing_config: AbstractWaningConfig,
                 repelling_config: AbstractWaningConfig = None,
                 blocking_config: AbstractWaningConfig = None,
                 insecticide_name: str = None):
        if not isinstance(killing_config, AbstractWaningConfig):
            raise ValueError(
                f"'killing_config' must be an AbstractWaningConfig instance, "
                f"got {type(killing_config).__name__}.")
        if blocking_config is not None and repelling_config is None:
            raise ValueError(
                "'blocking_config' requires 'repelling_config'. Blocking is applied to "
                "vectors that were not repelled, so both must be specified together.")
        if repelling_config is not None and not isinstance(repelling_config, AbstractWaningConfig):
            raise ValueError(
                f"'repelling_config' must be an AbstractWaningConfig instance, "
                f"got {type(repelling_config).__name__}.")
        if blocking_config is not None and not isinstance(blocking_config, AbstractWaningConfig):
            raise ValueError(
                f"'blocking_config' must be an AbstractWaningConfig instance, "
                f"got {type(blocking_config).__name__}.")

        self._campaign = campaign
        self._killing_config = killing_config
        self._repelling_config = repelling_config
        self._blocking_config = blocking_config
        self._insecticide_name = insecticide_name

        if blocking_config is not None:
            self._variant = "RBK"
        elif repelling_config is not None:
            self._variant = "RK"
        else:
            self._variant = "K"

    @property
    def variant(self) -> str:
        """The EMOD schema variant: ``"K"``, ``"RK"``, or ``"RBK"``."""
        return self._variant

    def require_variant(self, expected: str, intervention_name: str):
        """Validates that this effect has the correct variant for the consuming intervention.

        Args:
            expected: The required variant (``"K"``, ``"RK"``, or ``"RBK"``).
            intervention_name: Name of the intervention, used in the error message.

        Raises:
            ValueError: If the variant does not match.
        """
        if self._variant != expected:
            parts = {"K": "killing", "RK": "repelling + killing",
                     "RBK": "repelling + blocking + killing"}
            raise ValueError(
                f"{intervention_name} requires InsecticideWaningEffect with "
                f"{parts[expected]} configs (variant '{expected}'), but got variant "
                f"'{self._variant}' ({parts[self._variant]}).")

    def to_schema_dict(self) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults(
            self._VARIANT_SCHEMA[self._variant], schema_json=self._campaign.get_schema())
        obj.Killing_Config = self._killing_config.to_schema_dict(self._campaign)
        if self._repelling_config is not None:
            obj.Repelling_Config = self._repelling_config.to_schema_dict(self._campaign)
        if self._blocking_config is not None:
            obj.Blocking_Config = self._blocking_config.to_schema_dict(self._campaign)
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
    InsecticideWaningEffect]

for _ in __all_exports:
    _.__module__ = __name__

__all__ = [_.__name__ for _ in __all_exports]
