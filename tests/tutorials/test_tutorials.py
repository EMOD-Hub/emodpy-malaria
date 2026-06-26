import sys
import unittest
from pathlib import Path
import pytest

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
        experiment = t1.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 1 experiment failed.")

    def test_tutorial_2_reports(self):
        experiment = t2.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 2 experiment failed.")
        self._assert_reports("tutorial_2_results")

    def test_tutorial_3_interventions(self):
        experiment = t3.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 3 experiment failed.")
        self._assert_reports("tutorial_3_results")

    def test_tutorial_4_seasonality(self):
        experiment = t4.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 4 experiment failed.")
        self._assert_reports("tutorial_4_results")

    def test_tutorial_5_sweep(self):
        experiment = t5.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 5 experiment failed.")
        self._assert_reports("tutorial_5_results")

    def test_tutorial_7_burnin(self):
        experiment = t7b.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 7 burnin experiment failed.")

    def test_tutorial_7_pickup(self):
        experiment = t7p.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 7 pickup experiment failed.")

    def test_tutorial_8_migration(self):
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
