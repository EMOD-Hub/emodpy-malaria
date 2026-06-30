"""Climate configuration helpers for EMOD simulations.

These functions set the ``Climate_Model`` parameter and related settings
on the EMOD config object.  They are thin wrappers around direct parameter
assignment, providing validation and sensible defaults.
"""

from typing import Union

from emodpy_malaria.utils.emod_enum import ClimateModel, ClimateUpdateResolution


def set_climate_constant(config: object, *,
                         air_temperature: float = 27.0,
                         rainfall: float = 10.0,
                         relative_humidity: float = 0.75,
                         update_resolution: Union[ClimateUpdateResolution, str] = ClimateUpdateResolution.CLIMATE_UPDATE_DAY,
                         air_temperature_variance: float = 0.0,
                         relative_humidity_variance: float = 0.0,
                         enable_rainfall_stochasticity: bool = False):
    """Configure ``CLIMATE_CONSTANT`` mode with user-specified base values.

    EMOD uses these constant values (plus optional stochastic noise) for
    every node on every time step, ignoring any weather files.

    ``Base_Land_Temperature`` is set equal to *air_temperature* — EMOD
    requires it but does not use it for malaria simulations.

    ``Enable_Climate_Stochasticity`` is set automatically when any
    variance is non-zero or rainfall stochasticity is enabled.

    Args:
        config (object): The EMOD config object (``task.config``).
        air_temperature (float): Base air temperature in Celsius.
        rainfall (float): Base rainfall in mm/**update_resolution**.
        relative_humidity (float): Base relative humidity (0.0 -- 1.0).
        update_resolution (Union[ClimateUpdateResolution, str]): Climate update frequency.
        air_temperature_variance (float): Standard deviation (Celsius) for
            Gaussian noise on daily air temperature.
        relative_humidity_variance (float): Standard deviation (fraction) for
            Gaussian noise on daily relative humidity.
        enable_rainfall_stochasticity (bool): Draw daily **rainfall** from an
            exponential distribution with mean equal to the base value.
    """
    if not isinstance(update_resolution, ClimateUpdateResolution):
        try:
            update_resolution = ClimateUpdateResolution(update_resolution)
        except ValueError:
            raise ValueError(
                f"Invalid update_resolution {update_resolution!r}. "
                f"Valid options: {list(ClimateUpdateResolution)}"
            )

    stochastic = (air_temperature_variance != 0.0
                  or relative_humidity_variance != 0.0
                  or enable_rainfall_stochasticity)

    config.parameters.Climate_Model = ClimateModel.CLIMATE_CONSTANT
    config.parameters.Climate_Update_Resolution = update_resolution
    config.parameters.Base_Air_Temperature = air_temperature
    config.parameters.Base_Land_Temperature = air_temperature
    config.parameters.Base_Rainfall = rainfall
    config.parameters.Base_Relative_Humidity = relative_humidity
    config.parameters.Enable_Climate_Stochasticity = int(stochastic)
    config.parameters.Air_Temperature_Variance = air_temperature_variance
    config.parameters.Relative_Humidity_Variance = relative_humidity_variance
    config.parameters.Enable_Rainfall_Stochasticity = int(enable_rainfall_stochasticity)

    return config


def set_climate_by_data(config: object, *,
                        air_temperature_filename: str,
                        rainfall_filename: str,
                        relative_humidity_filename: str,
                        update_resolution: Union[ClimateUpdateResolution, str] = (
                            ClimateUpdateResolution.CLIMATE_UPDATE_DAY),
                        air_temperature_offset: float = 0.0,
                        air_temperature_variance: float = 0.0,
                        rainfall_scale_factor: float = 1.0,
                        enable_rainfall_stochasticity: bool = False,
                        relative_humidity_scale_factor: float = 1.0,
                        relative_humidity_variance: float = 0.0):
    """Configure ``CLIMATE_BY_DATA`` mode to read weather from binary files.

    EMOD reads four ``.bin`` / ``.bin.json`` file pairs for air temperature,
    land temperature, rainfall, and relative humidity.

    ``Enable_Climate_Stochasticity`` is set automatically when any
    variance is non-zero or rainfall stochasticity is enabled.

    Args:
        config (object): The EMOD config object (``task.config``).
        air_temperature_filename (str): Path to air temperature ``.bin`` file.
        rainfall_filename (str): Path to rainfall ``.bin`` file.
        relative_humidity_filename (str): Path to relative humidity ``.bin`` file.
        update_resolution (Union[ClimateUpdateResolution, str]): Climate update frequency.
        air_temperature_offset (float): Additive offset applied to all air
            temperature values (Celsius).
        air_temperature_variance (float): Standard deviation (Celsius) for
            Gaussian noise on daily air temperature.  If set to 0, relative humidity
            does not vary from the data. Set this to > 0 to enable stochasticity.
        rainfall_scale_factor (float): Multiplicative factor applied to all
            rainfall values.
        enable_rainfall_stochasticity (bool): When True, draw daily rainfall from an
            exponential distribution with mean equal to the data value.
        relative_humidity_scale_factor (float): Multiplicative factor applied to
            all relative humidity values.
        relative_humidity_variance (float): Standard deviation (fraction) for
            Gaussian noise on daily relative humidity. If set to 0, relative humidity
            does not vary from the data.
            Set this to > 0 to enable stochasticity.
    """
    if not isinstance(update_resolution, ClimateUpdateResolution):
        try:
            update_resolution = ClimateUpdateResolution(update_resolution)
        except ValueError:
            raise ValueError(
                f"Invalid update_resolution {update_resolution!r}. "
                f"Valid options: {list(ClimateUpdateResolution)}"
            )

    stochastic = (air_temperature_variance != 0.0
                  or relative_humidity_variance != 0.0
                  or enable_rainfall_stochasticity)

    config.parameters.Climate_Model = ClimateModel.CLIMATE_BY_DATA
    config.parameters.Climate_Update_Resolution = update_resolution

    config.parameters.Air_Temperature_Filename = str(air_temperature_filename)
    config.parameters.Land_Temperature_Filename = str(air_temperature_filename)
    config.parameters.Rainfall_Filename = str(rainfall_filename)
    config.parameters.Relative_Humidity_Filename = str(relative_humidity_filename)

    config.parameters.Air_Temperature_Offset = air_temperature_offset
    config.parameters.Land_Temperature_Offset = 0.0
    config.parameters.Rainfall_Scale_Factor = rainfall_scale_factor
    config.parameters.Relative_Humidity_Scale_Factor = relative_humidity_scale_factor

    config.parameters.Enable_Climate_Stochasticity = int(stochastic)
    config.parameters.Air_Temperature_Variance = air_temperature_variance
    config.parameters.Relative_Humidity_Variance = relative_humidity_variance
    config.parameters.Enable_Rainfall_Stochasticity = int(enable_rainfall_stochasticity)

    return config
