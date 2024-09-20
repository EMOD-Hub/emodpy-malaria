#!/usr/bin/python

from __future__ import print_function
import argparse
import emod_api.serialization.SerializedPopulation as SerPop
import emod_api.serialization.dtkFileSupport as dtk
from pathlib import Path
from typing import List

# VectorStateEnum defined in VectorEnums.h
STATE_INFECTIOUS = 0
STATE_INFECTED = 1  # implies female
STATE_ADULT = 2
STATE_MALE = 3
STATE_IMMATURE = 4
STATE_LARVA = 5
STATE_EGG = 6

Infection_Queues = ["InfectiousQueues", "InfectedQueues", "AdultQueues"]

# To be considered infection free an individual must have these values
UNINFECTED_HUMAN = {
    "infections": [],
    "infectiousness": 0,
    "m_is_infected": False,
    "m_female_gametocytes": 0,
    "m_female_gametocytes_by_strain": [],
    "m_male_gametocytes": 0,
    "m_gametocytes_detected": 0,
    "m_new_infection_state": 0
}


def zero_vector_infections(vector_pop_list: list, remove=False):
    """
    Resets infections in vectors or removes infections from vectors.

    Args:
        vector_pop_list: list of vector population in a node.
        remove: If True all infected vectors are removed from serialized population. If set to False (default) all
                vectors in the simulation are reset to state STATE_ADULT.
    Returns:
        None

    """
    for idx_vector_pop_list, vector_population in enumerate(vector_pop_list):
        # empty infections from all queues
        for queue in Infection_Queues:
            vec_population = vector_population[queue]["collection"]

            if remove:
                new_adult_queue_list = [cohort for cohort in vec_population if
                                        cohort.state != STATE_INFECTED and cohort.state != STATE_INFECTIOUS]
                vector_pop_list[idx_vector_pop_list][queue]["collection"] = new_adult_queue_list
            else:
                for cohort in vec_population:
                    assert (cohort['__class__'] == 'VectorCohortIndividual' or cohort['__class__'] == 'VectorCohort')
                    cohort.state = STATE_ADULT
                    cohort.progress = 0.0
                    cohort.m_pStrain = dtk.NullPtr()


def zero_human_infections(humans: List[dict], keep_ids: list = None):
    """
    Sets the infection state of individuals to uninfected.

    Args:
        humans: All humans in a node
        keep_ids: ids of individuals that will be skipped, i.e. infection state is not changed

    Returns:
        None

    """
    if not keep_ids:
        keep_ids = []
    for person in humans:
        if person.suid.id not in keep_ids:
            if all(key in person for key in UNINFECTED_HUMAN):
                person.update(UNINFECTED_HUMAN)
            else:
                missing_keys = set(UNINFECTED_HUMAN).difference(set(person))
                raise KeyError("Template Uninfected Human and human of serialized population differ in the following "
                               "key(s): ", missing_keys)


def zero_infections(source_filename: str, dest_filename: str, ignore_nodes: List[int], keep_individuals: List[int],
                    remove=False) -> None:
    """
    Removes/resets infections from humans and vectors.

    Args:
        source_filename: input file
        dest_filename: output file
        ignore_nodes: list of node ids. These nodes are skipped.
        keep_individuals: Ids of individuals. These individuals are skipped.
        remove: If true infections are removed from vectors, if false infections are reset.

    Returns:
        None
    """
    print('Ignoring nodes {0}'.format(ignore_nodes))
    print('Keeping infections in humans {0}'.format(keep_individuals))
    print("Reading file: '{0}'".format(source_filename))

    ser_pop = SerPop.SerializedPopulation(source_filename)

    for index, node in enumerate(ser_pop.nodes):
        print('Reading node {0} with node_id: {1}'.format(index, node.externalId))
        if node.externalId not in ignore_nodes:
            print('Zeroing vector infections')
            zero_vector_infections(node.m_vectorpopulations, remove)
            print('Zeroing human infections')
            zero_human_infections(node.individualHumans, keep_individuals)
        else:
            print('Ignoring node {0}'.format(index))

    # create output path if it doesn't exist
    out_path = Path(dest_filename).parent
    out_path.mkdir(parents=True, exist_ok=True)
    ser_pop.write(dest_filename)


def _get_paths(ser_paths: List[str], ser_date: List[str]) -> List[List[Path]]:
    """
    Get the path to all dtk files with a certain time stamp in a list of directories.
    Files with 'zero' in the name are skipped.

    Args:
        ser_paths: a list of directories to look into for *.dtk files
        ser_date: list of time stamps

    Returns:
        A list of paths to dtk files
    """
    print("ser_paths: ", ser_paths)
    files = []
    for s, serpath in enumerate(ser_paths):
        print('Processing simulation %d of %d' % (s + 1, len(ser_paths)))
        dtk_files = [x.name for x in Path(serpath).glob('*.dtk')]
        serialization_files = [Path(serpath, x) for x in dtk_files if
                               ('zero' not in x and any(map(lambda s: s in x, ser_date)))]

        for filename in serialization_files:
            output_filename = Path(filename.parent, filename.stem + '_zero' + filename.suffix)
            if output_filename.name in [x.name for x in Path(serpath).glob('*.dtk')]:
                print(output_filename.name, ' already zeroed')
                continue
            print('Found: {0}   Output: {1}'.format(filename, output_filename))
            files.append([filename, output_filename])
    return files


def zero_infection_path(in_out_paths: list, ser_date: list, ignore_nodeids: list = None, keep_humanids: list = None):
    """
    Loop over all .dtk files in ser_paths that have ser_date in the file name but not 'zero' and remove human and
     vector infections. '_zero' is appended to the output files.

    Args:
        in_out_paths: a list of lists of paths for directories to look into for .dtk files
        ser_date:  List of timestamps
        ignore_nodeids: list of nodes that are ignored
        keep_humanids: infections are not removed from these humans

    """
    if not ignore_nodeids:
        ignore_nodeids = []
    if not keep_humanids:
        keep_humanids = []
    file_paths = _get_paths(in_out_paths, ser_date)
    for in_path, out_path in file_paths:
        zero_infections(in_path, out_path, ignore_nodeids, keep_humanids)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Remove infections from individuals and vectors")
    parser.add_argument("-i", "--ignore", default=[], type=int, nargs="+", help="List of nodes that are ignored.")
    parser.add_argument("-k", "--keep", default=[], type=int, nargs="*",
                        help="List of individuals that keep their infections.")

    remove_from_file_group = parser.add_argument_group(title='Remove infections from one file')
    remove_from_file_group.add_argument("-s", "--source", help="input file", default=None)
    remove_from_file_group.add_argument("-d", "--destination", help="output file", default="output.dtk")

    remove_from_paths_group = parser.add_argument_group(title='Remove infections from all files in given paths')
    remove_from_paths_group.add_argument("-p", "--paths", default=[], nargs='+', type=Path,
                                         help="List of paths containing the dtk files.")
    remove_from_paths_group.add_argument("-t", "--time_stamps", default=[], nargs='+', type=str,
                                         help="List of timesteps. Filenames containing this timestep are "
                                              "processed, e.g. 001,021,365 ")

    args = parser.parse_args()

    # Not all combinations of parameters are  allowed
    if args.source and not (args.paths or args.time_stamps):
        zero_infections(args.source, args.destination, args.ignore, args.keep)

    elif args.paths and not args.source:
        zero_infection_path(args.paths, args.time_stamps, args.ignore, args.keep)

    else:
        parser.print_help()
        exit(0)
