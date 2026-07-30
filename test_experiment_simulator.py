import unittest

from experiment_simulator import SIMULATOR_EXPERIMENTS, _build_experiment_simulator_html


class ExperimentSimulatorTests(unittest.TestCase):
    def test_simulator_contains_ten_unique_experiments(self):
        self.assertEqual(len(SIMULATOR_EXPERIMENTS), 10)
        self.assertEqual(
            len({experiment["id"] for experiment in SIMULATOR_EXPERIMENTS}),
            len(SIMULATOR_EXPERIMENTS),
        )

    def test_simulator_configures_each_supported_control_type(self):
        control_types = {
            control["type"]
            for experiment in SIMULATOR_EXPERIMENTS
            for control in experiment["controls"]
        }

        self.assertEqual(control_types, {"range", "select", "toggle", "action"})

    def test_simulator_markup_contains_controls_and_canvas(self):
        markup = _build_experiment_simulator_html()

        self.assertIn("Acoustics experiments workbench", markup)
        self.assertIn('id="sim-canvas"', markup)
        self.assertIn("Hermann von Helmholtz", markup)
        self.assertIn("Don and Chips Davis", markup)
        self.assertIn("drawHelmholtz", markup)
        self.assertIn("drawDavis", markup)


if __name__ == "__main__":
    unittest.main()