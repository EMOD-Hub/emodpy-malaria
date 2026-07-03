import sys
import unittest
from pathlib import Path
import pytest

import matplotlib
matplotlib.use('Agg')

_tests_dir = str(Path(__file__).resolve().parents[1])
_tutorials_dir = str(Path(__file__).resolve().parents[2] / "tutorials")
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

import manifest  # noqa: E402, F401 — ensures tutorials pick up tests/manifest

if _tutorials_dir not in sys.path:
    sys.path.append(_tutorials_dir)

import tutorial_1_intro as t1  # noqa: E402
import tutorial_2_reports as t2  # noqa: E402
import tutorial_3_interventions as t3  # noqa: E402
import tutorial_4_seasonality as t4  # noqa: E402
import tutorial_5_sweep as t5  # noqa: E402
import tutorial_7_burnin as t7b  # noqa: E402
import tutorial_7_pickup as t7p  # noqa: E402
import tutorial_8_migration as t8  # noqa: E402


@pytest.mark.tutorial
class TestTutorials(unittest.TestCase):

    def test_tutorial_1_intro(self):
        t1.sim_years = 1
        experiment = t1.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 1 experiment failed.")

    def test_tutorial_2_reports(self):
        t2.sim_years = 1
        experiment = t2.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 2 experiment failed.")
        self._assert_reports("tutorial_2_results")

    def test_tutorial_3_interventions(self):
        t3.sim_years = 1
        experiment = t3.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 3 experiment failed.")

    def test_tutorial_4_seasonality(self):
        t4.sim_years = 1
        experiment = t4.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 4 experiment failed.")
        self._assert_reports("tutorial_4_results")

    def test_tutorial_5_sweep(self):
        t5.sim_years = 1
        experiment = t5.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 5 experiment failed.")
        self._assert_reports("tutorial_5_results")

    def test_tutorial_7_burnin(self):
        # serialize_years is read from manifest.burnin_serialize_years at import time;
        # tests/manifest.py sets burnin_serialize_years = 1 for fast tests.
        experiment = t7b.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 7 burnin experiment failed.")

    def test_tutorial_7_pickup(self):
        id_file = Path("experiment_id")
        self.assertTrue(id_file.exists(),
                        "experiment_id file not found — run test_tutorial_7_burnin first.")
        t7p.BURNIN_EXP_ID = id_file.read_text().strip()
        t7p.sim_years = 1
        experiment = t7p.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 7 pickup experiment failed.")

    def test_tutorial_8_migration(self):
        t8.sim_years = 1
        experiment = t8.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 8 experiment failed.")
        self._assert_reports("tutorial_8_results")

    def _assert_reports(self, output_path):
        results = Path(output_path)
        inset_charts = list(results.rglob("InsetChart.json"))
        self.assertGreater(len(inset_charts), 0,
                           f"InsetChart.json not found under {output_path}")


if __name__ == '__main__':
    unittest.main()
