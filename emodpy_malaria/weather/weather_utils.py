"""Utility functions for the weather module."""

import json
import numpy as np

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Union


def invert_dict(in_dict: dict, sort: bool = False, single_value: bool = False) -> dict:
    """Invert a dictionary by grouping keys by value.

    Example (single_value=False)::

        {1: 'a', 2: 'a', 3: 'b'}  ->  {'a': [1, 2], 'b': [3]}

    Args:
        in_dict: Dictionary to invert.
        sort: Sort resulting dict by key and value lists.
        single_value: Return only one representative key per unique value.
    """
    out_dict: dict = defaultdict(list)
    for k, v in in_dict.items():
        if isinstance(v, (list, tuple)):
            for vv in v:
                out_dict[vv].append(k)
        else:
            out_dict[v].append(k)

    if single_value:
        out_dict = {k: (v[0] if v else None) for k, v in out_dict.items()}

    if sort:
        out_dict = {k: sorted(v) for k, v in sorted(out_dict.items())}

    return dict(out_dict)


def hash_series(series) -> int:
    """Hash a numeric series for uniqueness detection."""
    return hash(np.array(series).tobytes())


def save_json(content: dict, file_path: Union[str, Path]) -> None:
    """Write a dictionary to a JSON file."""
    with open(str(file_path), "wt") as f:
        json.dump(content, f, indent=2, separators=(",", ": "))


def make_path(dir_path: Union[str, Path]) -> None:
    """Create directories if they don't exist."""
    if dir_path:
        Path(dir_path).mkdir(exist_ok=True, parents=True)


def ymd(date_arg: datetime) -> str:
    """Format datetime as YYYYMMDD string."""
    return date_arg.strftime("%Y%m%d")


def parse_date(date_arg: Union[int, str], default_month: int, default_day: int) -> datetime:
    """Parse a date from year (2018), day-of-year (2018001), or YYYYMMDD (20180101) format."""
    date_str = str(date_arg)
    if not date_str.isdigit():
        raise ValueError(f"Invalid date string {date_arg!r}. Only digits are allowed.")

    if len(date_str) == 4:
        return datetime(int(date_str), default_month, default_day)
    elif len(date_str) == 7:
        return datetime.strptime(date_str, "%Y%j")
    elif len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d")
    else:
        raise ValueError(
            f"Date string {date_str!r} is not in a supported format "
            f"(YYYY, YYYYDDD, or YYYYMMDD)."
        )


def validate_str_value(value: str) -> None:
    """Raise if value is None or empty."""
    if not value:
        raise ValueError("String value must not be None or empty.")
