"""Serialization configuration helpers for EMOD burnin/pickup workflows.

Typical workflow:

1. **Burnin phase** -- call ``configure_serialization_write`` to save
   population state at specified time steps.
2. **Pickup phase** -- call ``get_burnin_sim_outpaths`` to resolve
   output paths, then ``configure_serialization_read`` to load state.

See ``emodpy_malaria.serialization`` for inspecting and modifying
``.dtk`` files after they have been written.
"""
import logging
import os
from typing import Optional, Union

import pandas as pd
from emodpy.utils.emod_enum import StrEnum

logger = logging.getLogger(__name__)

__all__ = [
    "SerializationPrecision",
    "configure_serialization_write",
    "configure_serialization_read",
    "get_burnin_sim_outpaths",
]


class SerializationPrecision(StrEnum):
    REDUCED = "REDUCED"
    FULL = "FULL"


def configure_serialization_write(
    config: object,
    *,
    time_steps: list[int] = None,
    times: list[float] = None,
    precision: Union[SerializationPrecision, str] = SerializationPrecision.REDUCED,
    mask_node_write: int = 0,
    max_humans_per_collection: int = 2000,
):
    """Configure a simulation to **write** serialized population files.

    Sets ``Serialized_Population_Writing_Type`` to ``TIMESTEP`` or ``TIME``
    and disables reading. Provide exactly one of *time_steps* or *times*.

    Args:
        config: The config object (``task.config``).
        time_steps: Simulation time steps at which to serialize.
            ``0`` = initial state, ``n`` = after the *n*-th time step.
            Sets ``Serialized_Population_Writing_Type = "TIMESTEP"``.
        times: Absolute simulation times at which to serialize (rounded
            up to the nearest time step internally by EMOD).
            Sets ``Serialized_Population_Writing_Type = "TIME"``.
        precision: Floating-point precision for the serialized file.
            ``REDUCED`` (default) produces smaller files; ``FULL`` preserves
            full precision.
        mask_node_write: Bitmask controlling what data is saved.
            ``0`` saves everything. ``16`` skips saving larval habitat data, which will then be loaded
            from species config on read.
        max_humans_per_collection: Maximum number of human agents saved per
            collection in the serialized file. Higher values are faster to
            read/write but use more memory. Default 2000.
    """
    if time_steps is not None and times is not None:
        raise ValueError("Provide either time_steps or times, not both.")
    if time_steps is None and times is None:
        raise ValueError("Provide either time_steps or times.")

    if not isinstance(precision, SerializationPrecision):
        try:
            precision = SerializationPrecision(precision)
        except ValueError:
            raise ValueError(
                f"Invalid precision {precision!r}. "
                f"Valid options: {[e.value for e in SerializationPrecision]}")

    if mask_node_write not in (0, 16):
        raise ValueError(
            f"mask_node_write must be 0 (save everything) or 16 (skip larval "
            f"habitat data), got {mask_node_write!r}.")

    config.parameters.Serialized_Population_Reading_Type = "NONE"

    if time_steps is not None:
        config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"
        config.parameters.Serialization_Time_Steps = sorted(time_steps)
        config.parameters.Serialization_Times = []
    else:
        config.parameters.Serialized_Population_Writing_Type = "TIME"
        config.parameters.Serialization_Times = sorted(times)
        config.parameters.Serialization_Time_Steps = []

    config.parameters.Serialization_Precision = str(precision)
    config.parameters.Serialization_Mask_Node_Write = mask_node_write
    config.parameters.Serialization_Max_Humans_Per_Collection = max_humans_per_collection

    return config


def configure_serialization_read(
    config: object,
    *,
    path: str,
    filenames: list[str],
    mask_node_read: int = 0,
    enable_random_generator_from_serialized: bool = False,
):
    """Configure a simulation to **read** a serialized population at startup.

    Sets ``Serialized_Population_Reading_Type = "READ"`` and disables
    writing.

    Args:
        config: The config object (``task.config``).
        path: Root directory containing the ``.dtk`` file(s).
            This must be a path that EMOD can reach at runtime — use
            :func:`get_burnin_sim_outpaths` to obtain platform-correct paths.
        filenames: ``.dtk`` filename(s) to load. The number of
            filenames must match the number of cores used for the simulation.
        mask_node_read: Bitmask controlling what data is loaded.
            ``0`` loads everything. ``16`` skips larval habitat data
            (habitats will be read from species config instead).
        enable_random_generator_from_serialized: If ``True``, the random
            number generator state is restored from the serialized file,
            producing an exact continuation of the original simulation.
    """
    if mask_node_read not in (0, 16):
        raise ValueError(
            f"mask_node_read must be 0 (load everything) or 16 (skip larval "
            f"habitat data), got {mask_node_read!r}.")

    config.parameters.Serialized_Population_Writing_Type = "NONE"
    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialized_Population_Path = path
    config.parameters.Serialized_Population_Filenames = list(filenames)
    config.parameters.Serialization_Mask_Node_Read = mask_node_read
    config.parameters.Enable_Random_Generator_From_Serialized_Population = (
        1 if enable_random_generator_from_serialized else 0
    )

    return config


def get_burnin_sim_outpaths(
    experiment_id: str,
    platform: object,
    *,
    tag_columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Resolve platform-correct output paths for each simulation in a burnin experiment.

    Returns a DataFrame with at least ``sim_id`` and ``outpath`` columns.
    ``outpath`` is the value to pass as *population_path* to
    :func:`configure_serialization_read` — it already points to each
    simulation's ``output/`` directory using a path that the pickup
    simulation's EMOD process can reach (container-mapped, COMPS working
    directory, or local filesystem path as appropriate).

    Args:
        experiment_id: The burnin experiment ID.
        platform: The idmtools ``Platform`` object for the pickup run.
            The platform type determines how paths are resolved:

            - **COMPS** — converts the HPC working directory to a
              ``/mnt/...`` UNC path and appends ``/output``.
            - **Container** — maps the host-side simulation directory into
              the container mount namespace via ``map_container_path``.
            - **Slurm / File** — uses the absolute host filesystem path.

        tag_columns: Optional simulation tag names to include as extra
            columns in the returned DataFrame (e.g. ``["Run_Number"]``).

    Returns:
        DataFrame sorted by ``sim_id`` with columns ``sim_id``, ``outpath``, plus any requested *tag_columns*.
    """
    from idmtools.entities.experiment import Experiment

    platform_type = platform.get_platform_type()

    children = (["tags", "configuration", "files", "hpc_jobs"]
                if platform_type == "COMPS"
                else ["tags", "configuration"])

    exp = Experiment.from_id(experiment_id, children=False)
    exp.simulations = platform.get_children(exp.id, exp.item_type, children=children)

    records = []
    for sim in exp.simulations:
        outpath = _resolve_sim_outpath(sim, platform, platform_type)
        record = {"sim_id": str(sim.id), "outpath": outpath}
        if tag_columns:
            for col in tag_columns:
                record[col] = sim.tags.get(col)
        records.append(record)

    df = pd.DataFrame(records).sort_values("sim_id").reset_index(drop=True)
    return df


def _resolve_sim_outpath(sim, platform, platform_type: str) -> str:
    """Return the EMOD-reachable output path for a single simulation."""
    if platform_type == "COMPS":
        return _resolve_comps_outpath(sim)
    elif hasattr(platform, "data_mount"):
        return _resolve_container_outpath(sim, platform)
    else:
        return _resolve_file_outpath(sim)


def _resolve_comps_outpath(sim) -> str:
    path = sim.get_platform_object().hpc_jobs[0].working_directory
    path = path.replace("\\", "/")
    path = path.replace("internal.idm.ctr", "mnt")
    path = path.replace("IDM2", "idm2")
    return path + "/output"


def _resolve_container_outpath(sim, platform) -> str:
    from idmtools_platform_container.utils.general import map_container_path
    host_path = str(sim.get_directory())
    container_path = map_container_path(
        platform.job_directory, platform.data_mount, host_path
    )
    return container_path + "/output"


def _resolve_file_outpath(sim) -> str:
    return os.path.join(str(sim.get_directory()), "output")
