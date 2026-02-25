"""
The module for weather utility functions.
"""

import numpy as np
import json

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, NoReturn, Union


def invert_dict(in_dict: Dict, sort=False, single_value=False) -> Dict:
    """
    Invert a dictionary by grouping keys by value. In the resulting dictionary keys are unique value from the original
    dictionary (including individual element of value lists) and values are lists of original dictionary keys.
    The function is used for grouping nodes by offset or weather time series hash, and determining unique series.

    For example,
        single_value = False (default)
            {1: [11, 22], 2: [22], 3: [11]} -> {11: [1, 3], 22: [1, 2]}
        single_value = True
            {1: [11, 22], 2: [22], 3: [11]} -> {11: 1, 22: 1}

    Args:
        in_dict: Input dictionary to be inverted.
        sort: Sort the resulting dictionary by key and value.
        single_value: Only return a single representative "original key" (from in_dict)
                        for each corresponding unique "original value" (from in_dict).

    Returns:
        Inverted dictionary where
            (single_value = False): keys are "original values" and values are lists of corresponding "original keys"
            (single_value = True):  keys are "original values" and values is a single representative "original key".
    """
    # Init the output dictionary to be able to collect original dictionary keys per value element.
    out_dict = defaultdict(list)
    # For each unique value append the corresponding key.
    for k, v in in_dict.items():
        if isinstance(v, Iterable):
            # In case original dictionary values are lists.
            for vv in v:
                out_dict[vv].append(k)
        else:
            # In case the original dictionary value are not lists.
            out_dict[v].append(k)

    if single_value:
        # Transform the output dictionary to only take have a single value (instead od a list, for each value).
        out_dict = {k: None if len(v) == 0 else v[0] for k, v in out_dict.items()}

    if sort:
        # Ensure the output  dictionary is sorted by key, value.
        out_dict = {k: sorted(v) for k, v in sorted(out_dict.items())}

    return dict(out_dict)       # Convert from defaultdict to a regular dictionary


def hash_series(series: Iterable[np.float32]) -> int:
    """
    Calculate a unique hash for each input series. Used for grouping nodes by weather time series.

    Args:
        series: The list or array of float values.

    Returns:
        Series hash value as int.
    """
    h = hash(np.array(series).tobytes())
    return h


def save_json(content: Dict[str, str], file_path: Union[str, Path]) -> NoReturn:
    """
    Save dictionary to a json file.

    Args:
        content: Content in the form of a dictionary.
        file_path: The path of the output weather metadata file.

        Returns:
            None

    """
    with open(str(file_path), "wt") as file:
        json.dump(content, file, indent=2, separators=(",", ": "))


def make_path(dir_path: Union[str, Path]) -> NoReturn:
    """Make path directories."""
    if dir_path:
        Path(dir_path).mkdir(exist_ok=True, parents=True)


def ymd(date_arg: datetime) -> str:
    """Convert datetime into a string of format yyyymmdd."""
    return date_arg.strftime("%Y%m%d")


def parse_date(date_arg: Union[int, str], default_month: int, default_day: int) -> datetime:
    date_str = str(date_arg)
    if not all([v.isdigit() for v in date_str]):
        raise ValueError("Invalid date string {}. Only digits are allowed.".format(date_arg))

    if len(date_str) == 4:
        result = datetime(int(date_str), default_month, default_day)

    elif len(date_str) == 7:
        result = datetime.strptime(date_str, '%Y%j')

    elif len(date_str) == 8:
        result = datetime.strptime(date_str, '%Y%m%d')

    else:
        raise ValueError("The date string {} is not in one of the supported formats (e.g. 2015, 2015365, 20151231)."
                         .format(date_str))

    return result


def validate_str_value(value: str) -> NoReturn:
    """Assert a string value is not None or empty."""
    assert value, "Value name must be specified."
