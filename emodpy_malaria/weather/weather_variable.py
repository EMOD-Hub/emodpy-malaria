"""Weather variable enum for the four EMOD climate inputs."""

from __future__ import annotations

from enum import Enum


class WeatherVariable(Enum):
    """Weather variables required by EMOD.

    Each variable corresponds to a pair of binary (``.bin``) and metadata
    (``.bin.json``) files that EMOD reads when ``Climate_Model`` is set to
    ``CLIMATE_BY_DATA``.
    """
    AIR_TEMPERATURE = "airtemp"
    RELATIVE_HUMIDITY = "humidity"
    RAINFALL = "rainfall"
    LAND_TEMPERATURE = "landtemp"

    def __hash__(self):
        return hash(self.name + self.value)

    @classmethod
    def list(cls, exclude: "WeatherVariable | list[WeatherVariable] | None" = None) -> list["WeatherVariable"]:
        """Return all weather variables, optionally excluding some.

        Args:
            exclude: Variable(s) to exclude from the list.
        """
        exclude = exclude or []
        if isinstance(exclude, WeatherVariable):
            exclude = [exclude]
        if not isinstance(exclude, list):
            raise TypeError("exclude must be a WeatherVariable or list of WeatherVariable.")
        return [v for v in cls if v not in exclude]

    @classmethod
    def validate_types(cls, value_dict: dict["WeatherVariable", object] | None,
                       value_types: type | list[type] | None = None) -> None:
        """Validate that dict keys are WeatherVariable and values match the given type(s)."""
        if value_dict is None:
            return
        if not isinstance(value_dict, dict):
            raise TypeError("Expected a dictionary.")
        for variable, item in value_dict.items():
            if not isinstance(variable, WeatherVariable):
                raise TypeError("Dictionary keys must be WeatherVariable instances.")
            if value_types is not None:
                types = value_types if isinstance(value_types, list) else [value_types]
                if not any((tp is None and item is None) or (tp is not None and isinstance(item, tp))
                           for tp in types):
                    raise TypeError(f"Dictionary values must be of type {types}, got {type(item)}.")
