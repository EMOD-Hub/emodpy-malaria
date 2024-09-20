#!/usr/bin/env python3

import pytest
from pathlib import Path
import sys
sys.path.append('../../emodpy_malaria/serialization')
import zero_infections
import emod_api.serialization.SerializedPopulation as SerPop
import emod_api.serialization.dtkFileSupport as dtk
import copy

my_dir = None

Path_dtk_Files = Path("..", "burnin_create_infections", "serialization_files", "output", "state-00050.dtk")

@pytest.fixture(scope="session")
def create_test_dir(tmp_path_factory):
    root_path = tmp_path_factory.mktemp("PYTEST_TMPDIR")

    # create dummy dirs
    p1 = Path(root_path / 'temp1')
    Path.mkdir(p1)
    p2 = Path(root_path / 'temp2')
    Path.mkdir(p2)

    # create dummy files
    Path(p1, 'state-00123.dtk').write_text('Dummy dtk file')
    Path(p1, 'state-00365.dtk').write_text('Dummy dtk file')
    Path(p1, 'state-00123.dtk').write_text('Dummy dtk file')
    Path(p2, 'state-00365.dtk').write_text('Dummy dtk file')

    return [p1, p2]


def _count_infections(serialized_pop):
    """
    Counts the total number of cohorts and cohorts with infections.

    Args:
        serialized_pop: A serialized population

    Returns:
        Total number of cohorts and the ids of cohorts with infections

    """
    infected_cohort_ids = set()
    count_cohorts = 0
    for node in serialized_pop.nodes:
        for vectors in node.m_vectorpopulations:
            for q in zero_infections.Infection_Queues:
                for cohort in vectors[q].collection:
                    count_cohorts += 1
                    if cohort.state == zero_infections.STATE_INFECTED or cohort.state == zero_infections.STATE_INFECTIOUS:
                        infected_cohort_ids.add(cohort.m_ID)
    return count_cohorts, infected_cohort_ids


def test_get_paths(create_test_dir: pytest.TempdirFactory):
    paths = create_test_dir
    files = zero_infections._get_paths(paths, ['00100', '00365'])
    print("Input        ,            Output:")
    [print(f) for f in files]
    assert len(files[0]) == 2   # only two paths, one input and output file found
    assert len(files[1]) == 2   # only two paths, one input and output file found
    assert files[0][0].match('temp1/state-00365.dtk')
    assert files[0][1].match('temp1/state-00365_zero.dtk')
    assert files[1][0].match('temp2/state-00365.dtk')
    assert files[1][1].match('temp2/state-00365_zero.dtk')


def test_zero_human_infections_exception():
    source = Path_dtk_Files
    ser_pop = SerPop.SerializedPopulation(source)
    individuals = [copy.copy(ser_pop.nodes[0].individualHumans[0])]
    del individuals[0]["m_new_infection_state"]

    with pytest.raises(KeyError) as e_info:
        zero_infections.zero_human_infections(individuals)

    assert "Template Uninfected Human" in e_info.value.args[0]
    assert '{\'m_new_infection_state\'}' == str(e_info.value.args[1])


def test_zero_human_infections():
    uninfected_human = zero_infections.UNINFECTED_HUMAN
    
    total_infected = 0
    source = Path_dtk_Files
    destination = "test_out_state-00365.dtk"
    ser_pop = SerPop.SerializedPopulation(source)
    for node in ser_pop.nodes:
        for human in node.individualHumans:
            # cont number of infected human
            if not all([human[attribute] == uninfected_human[attribute] for attribute in uninfected_human]):
                total_infected += 1

    print("Number infected humans: ", total_infected)
    assert total_infected > 0  # at least one infection must be present

    for node in ser_pop.nodes:
        zero_infections.zero_human_infections(node.individualHumans)

    ser_pop.write(destination)

    # load saved file and check infections
    test_pop = SerPop.SerializedPopulation(destination)
    for node in test_pop.nodes:
        for human in node.individualHumans:
            # no human may show a sign of infection
            if not all([human[attribute] == uninfected_human[attribute] for attribute in uninfected_human]):
                assert False


def test_zero_vector_infections_dont_remove():
    source = Path_dtk_Files
    destination = "test_out_state-00365.dtk"
    pre_pop = SerPop.SerializedPopulation(source)
    count_cohorts_before, infected_cohort_ids = _count_infections(pre_pop)

    print("count_cohorts_before zeroing: ", count_cohorts_before)
    assert len(infected_cohort_ids) > 0  # at least one infection must be present

    for node in pre_pop.nodes:
        zero_infections.zero_vector_infections(node.m_vectorpopulations)

    pre_pop.write(destination)

    count_cohorts_after = 0
    zeroed_pop = SerPop.SerializedPopulation(destination)
    for node in zeroed_pop.nodes:
        for vector_population in node.m_vectorpopulations:
            queues = [vector_population.InfectiousQueues.collection, vector_population.InfectedQueues.collection,
                      vector_population.AdultQueues.collection]
            for cohort in queues:
                for vc in cohort:
                    count_cohorts_after += 1
                    infected_cohort_ids.discard(vc.m_ID)
                    assert(vc.state == zero_infections.STATE_ADULT)
                    assert(vc.progress == 0.0)
                    assert(vc.m_pStrain == dtk.NullPtr())   # comparing dicts

    assert not infected_cohort_ids    # were all infected cohorts zeroed?
    assert count_cohorts_before == count_cohorts_after  # no cohort was removed


def test_zero_vector_infections_remove():
    source = Path_dtk_Files
    destination = "test_out_remove_state-00365.dtk"

    pre_pop = SerPop.SerializedPopulation(source)
    count_cohorts_before, m_Ids = _count_infections(pre_pop)
    assert len(m_Ids) > 0  # at least one infection must be present

    for node in pre_pop.nodes:
        zero_infections.zero_vector_infections(node.m_vectorpopulations, remove=True)

    pre_pop.write(destination)

    test_pop = SerPop.SerializedPopulation(destination)

    for n in test_pop.nodes:
        for vectors in n.m_vectorpopulations:
            queues = [vectors.InfectiousQueues.collection, vectors.InfectedQueues.collection,
                      vectors.AdultQueues.collection]
            for cohort in queues:
                for vc in cohort:
                    assert (vc.state != zero_infections.STATE_INFECTIOUS)
                    assert (vc.state != zero_infections.STATE_INFECTED)
                    assert (vc.m_ID not in m_Ids)


if __name__ == '__main__':
    pytest.main()
