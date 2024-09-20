#!/usr/bin/env python3

"""
Weather variable module implement functionality for working with weather variables.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, NoReturn, Union


class WeatherVariable(Enum):
    """Weather variables required by EMOD."""
    # TODO: Consider whether ground temperature.
    AIR_TEMPERATURE = "airtemp"
    RELATIVE_HUMIDITY = "humidity"
    RAINFALL = "rainfall"
    LAND_TEMPERATURE = "landtemp"

    def __hash__(self):
        """Hash method for a WeatherVariable object."""
        return hash(self.name + self.value)

    @classmethod
    def list(cls, exclude: Union[WeatherVariable, List[WeatherVariable]] = None) -> List[WeatherVariable]:
        """
        List of all weather variables or a subset if 'exclude' argument is used.

        Args:
            exclude: (Optional) List of weather variables to be excluded.

        Returns:
            List of all or a subset of weather variables.
        """
        exclude = exclude or []
        exclude = [exclude] if isinstance(exclude, WeatherVariable) else exclude
        if not isinstance(exclude, List) or len(exclude) > 0 and not isinstance(exclude[0], WeatherVariable):
            raise TypeError("Exclude variable tpy is not a list of WeatherVariable.")

        items = [cls.AIR_TEMPERATURE, cls.RELATIVE_HUMIDITY, cls.RAINFALL, cls.LAND_TEMPERATURE]
        return [t for t in items if t not in exclude]

    @classmethod
    def validate_types(cls,
                       value_dict: Dict[WeatherVariable, Any],
                       value_types: Union[Any, List[Any]] = None) -> NoReturn:
        """
        Validate dictionary keys are of type WeatherVariable and values are of specified type.

        Args:
            value_dict: Dictionary to be validated.
            value_types: Dictionary value types.

        Returns:
            None
        """
        if value_dict is None:
            return

        if not isinstance(value_dict, Dict):    # Main object must be a dict
            raise TypeError("Not a dictionary.")

        for variable, item in value_dict.items():
            if not isinstance(variable, WeatherVariable):   # Keys must be WeatherVariable
                raise TypeError("Keys are not of WeatherVariable type.")

            if value_types is not None:
                value_types: Union[Any, List[Any]] = value_types if isinstance(value_types, Iterable) else [value_types]
                type_ok = [tp is None and item is None for tp in value_types if not tp]   # is None if specified
                type_ok.extend([isinstance(item, tp) for tp in value_types if tp])        # is instance of a type
                if all([not t for t in type_ok]):                                         # if all type tests are false
                    raise TypeError(f"Values must be of type {str(value_types)}.")
