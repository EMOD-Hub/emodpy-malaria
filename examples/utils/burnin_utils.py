import copy
import os
from typing import List, Dict

import pandas as pd
from COMPS import AuthManager
from COMPS.Data import QueryCriteria, Simulation
from idmtools.core import ItemType
from idmtools.entities.iplatform import IPlatform


def _get_serialized_filenames(num_cores, timesteps):
    if num_cores == 1:
        serialized_list = [f"state-{str(timesteps).zfill(5)}.dtk"]
    else:
        serialized_list = [f"state-{str(timesteps).zfill(5)}-{str(core_count).zfill(3)}.dtk"
                           for core_count in range(num_cores)]
    return serialized_list

def _get_core_counts(sim_id, platform):
    num_cores = 1
    if type(platform).__name__ == 'COMPSPlatform':
        sim = platform.get_item(sim_id, ItemType.SIMULATION, raw=True)
        sim.refresh(QueryCriteria().select_children('hpc_jobs'))
        num_cores = int(sim.hpc_jobs[-1].configuration.max_cores)
    elif type(platform).__name__ == 'ContainerPlatform' or type(platform).__name__ == 'SlurmPlatform':
        num_cores = platform.ntasks if platform.ntasks is not None else 1
        # print("num_cores:", num_cores) 
    return num_cores


def get_workdir_from_simulations(platform: 'IPlatform', comps_simulations: List[Simulation]) -> Dict[str, str]:
    """
    Get COMPS filepath
    Args:
        platform: idmtools Platform
        comps_simulations: COMPS Simulations
    Returns: dictionary with simid as key and filepath as value
    """

    if platform.environment.upper() == "SLURMSTAGE" or platform.environment.upper() == "CALCULON":
        mounts = AuthManager.get_environment_macros(platform.environment)['DOCKER_MOUNTS']
        mounts = {v[0]: v[1:4] for v in [m.split(';') for m in mounts.split('|')]}
        # pretend I'm on Linux and set the Linux mapping environment variables
        for k, v in mounts.items():
            os.environ[k] = ';'.join([v[0], v[2]])
    sim_work_dir = {str(sim.id): sim.hpc_jobs[-1].working_directory for sim in comps_simulations if sim.hpc_jobs}

    return sim_work_dir


def create_sim_directory_map(exp_id: str, platform: 'IPlatform'):
    """
        Return a dataframe which contains simulation's working_path and tags.
    Args:
        exp_id: experiment id
        platform: idmtools platform
    Returns:
        dataframe
    """
    # Get idmtools Experiment
    exp = platform.get_item(exp_id, ItemType.EXPERIMENT, raw=False)
    tags_list = []
    for sim in exp.simulations:
        tags = copy.deepcopy(sim.tags)
        tags.update(dict(simid=sim.id))
        tags_list.append(tags)
    df = pd.DataFrame(tags_list)

    if len(df) != len(exp.simulations):
        print(f'Warning: not all jobs in {exp_id} succeeded', ':', )
        print(len(exp.simulations) - len(df), 'unsucceeded')

    simulations = exp.simulations
    dir_list = []
    for sim in simulations:
        dir_dict = {"simid": str(sim.id), "serialized_file_path": platform.get_directory(sim)}
        dir_list.append(dir_dict)

    df_dir = pd.DataFrame(dir_list)
    df = pd.merge(left=df, right=df_dir, on='simid')

    return df


def build_burnin_df(exp_id: str, platform, serialize_days):
    """
    return dataframe which contains outpath, serialized_population_filenames
    Args:
        exp_id:
        platform:
        serialize_days:
    Returns:
        dataframe:
        Run_Number | Serialization_Time_Steps | task_type | sweep_tag | simid | outpath|Num_Cores|Serialized_Population_Filenames
    Note, Serialized_Population_Filenames depends on n_cores. if n_cores = 2, Serialized_Population_Filenames look
    like these: state-00050-000.dtk, state-00050-001.dtk
    """

    df = platform.create_sim_directory_df(exp_id)
    # add Num_Cores to df
    df["Num_Cores"] = df["simid"].apply(_get_core_counts, platform=platform)

    #try:
    burnin_length_in_days = serialize_days #int(df["Serialization_Time_Steps"].iloc[0].strip('[]'))
    #except AttributeError:
        # different versions of pandas save this as either a string or a list
        #burnin_length_in_days = df["Serialization_Time_Steps"].iloc[0][-1]

    df["Serialized_Population_Filenames"] = df["Num_Cores"].apply(_get_serialized_filenames, timesteps=burnin_length_in_days)
    df = df.reset_index(drop=True)
    # Assuming df is your DataFrame
    df.to_csv('serilized_output.csv', index=False)
    return df
