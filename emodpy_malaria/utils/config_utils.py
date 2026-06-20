def non_schema_checks(config):
    """
    Do additional voluntary checks for config consistency beyond what the schema validates.
    """
    p = config.parameters
    if hasattr(p, 'Simulation_Type') and p.Simulation_Type != 'MALARIA_SIM':
        raise ValueError(f"Simulation_Type must be 'MALARIA_SIM', got '{p.Simulation_Type}'")
    return


def validate_bins(bins: list, param_name: str, min_value: float = None, max_value: float = None) -> list:
    """
    Validate that a list of bin edges is in strictly ascending order and within optional bounds.

    Args:
        bins (list): List of numeric bin edges.
        param_name (str): Name of the parameter (for error messages).
        min_value (float): If set, all values must be >= this.
        max_value (float): If set, all values must be <= this.

    Returns:
        The validated list of bins.

    Raises:
        ValueError: If bins are not in ascending order or out of bounds.
    """
    if not bins:
        return bins
    for i in range(1, len(bins)):
        if bins[i] <= bins[i - 1]:
            raise ValueError(
                f"{param_name} must be in strictly ascending order, "
                f"but got {bins[i]} at index {i} after {bins[i - 1]} at index {i - 1}.")
    if min_value is not None and bins[0] < min_value:
        raise ValueError(
            f"{param_name} values must be >= {min_value}, but got {bins[0]}.")
    if max_value is not None and bins[-1] > max_value:
        raise ValueError(
            f"{param_name} values must be <= {max_value}, but got {bins[-1]}.")
    return bins
