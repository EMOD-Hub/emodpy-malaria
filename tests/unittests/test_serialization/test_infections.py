"""Unit tests for emodpy_malaria.serialization._infections."""

import pytest

from emodpy_malaria.serialization._infections import (
    zero_human_infections,
    zero_vector_infections,
    UNINFECTED_HUMAN_TEMPLATE,
    STATE_INFECTIOUS,
    STATE_INFECTED,
    STATE_ADULT,
)


class MockAttrDict(dict):
    """Dict that also supports attribute access, like SerialObject."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


def _make_human(suid_id, infected=True, num_infections=1):
    """Create a mock human individual."""
    infections = [{"suid": {"id": i}} for i in range(num_infections)] if infected else []
    return MockAttrDict({
        "suid": MockAttrDict({"id": suid_id}),
        "infections": infections,
        "infectiousness": 0.5 if infected else 0,
        "m_is_infected": infected,
        "m_female_gametocytes": 100 if infected else 0,
        "m_female_gametocytes_by_strain": [{"strain": 1}] if infected else [],
        "m_male_gametocytes": 50 if infected else 0,
        "m_gametocytes_detected": 1 if infected else 0,
        "m_new_infection_state": 1 if infected else 0,
    })


def _make_vector_cohort(state, class_name="VectorCohortIndividual"):
    return MockAttrDict({
        "__class__": class_name,
        "state": state,
        "progress": 0.5,
        "m_pStrain": {"some": "strain"},
        "m_OocystCohorts": [],
        "m_SporozoiteCohorts": [],
    })


def _make_vector_population():
    return MockAttrDict({
        "InfectiousQueues": {"collection": [
            _make_vector_cohort(STATE_INFECTIOUS),
        ]},
        "InfectedQueues": {"collection": [
            _make_vector_cohort(STATE_INFECTED),
            _make_vector_cohort(STATE_INFECTED),
        ]},
        "AdultQueues": {"collection": [
            _make_vector_cohort(STATE_ADULT),
            _make_vector_cohort(STATE_ADULT),
        ]},
    })


@pytest.mark.unit
class TestZeroHumanInfections:
    def test_zeros_all_humans(self):
        humans = [_make_human(1), _make_human(2), _make_human(3)]
        count = zero_human_infections(humans)
        assert count == 3
        for h in humans:
            assert h["infections"] == []
            assert h["m_is_infected"] is False
            assert h["m_female_gametocytes"] == 0
            assert h["m_male_gametocytes"] == 0

    def test_keeps_specified_ids(self):
        humans = [_make_human(1), _make_human(2), _make_human(3)]
        count = zero_human_infections(humans, keep_ids=[2])
        assert count == 2
        assert humans[1]["m_is_infected"] is True
        assert humans[0]["m_is_infected"] is False

    def test_uninfected_humans_still_counted(self):
        humans = [_make_human(1, infected=False)]
        count = zero_human_infections(humans)
        assert count == 1

    def test_missing_key_raises(self):
        bad_human = MockAttrDict({
            "suid": MockAttrDict({"id": 1}),
            "infections": [],
        })
        with pytest.raises(KeyError):
            zero_human_infections([bad_human])


@pytest.mark.unit
class TestZeroVectorInfections:
    def test_reset_mode(self):
        vp_list = [_make_vector_population()]
        count = zero_vector_infections(vp_list, remove=False)
        assert count == 3

        for cohort in vp_list[0]["InfectiousQueues"]["collection"]:
            assert cohort.state == STATE_ADULT
            assert cohort.progress == 0.0

        for cohort in vp_list[0]["InfectedQueues"]["collection"]:
            assert cohort.state == STATE_ADULT

        assert len(vp_list[0]["AdultQueues"]["collection"]) == 2

    def test_remove_mode(self):
        vp_list = [_make_vector_population()]
        count = zero_vector_infections(vp_list, remove=True)
        assert count == 3

        assert len(vp_list[0]["InfectiousQueues"]["collection"]) == 0
        assert len(vp_list[0]["InfectedQueues"]["collection"]) == 0
        assert len(vp_list[0]["AdultQueues"]["collection"]) == 2
