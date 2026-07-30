import unittest

from digital_lab import DIGITAL_LAB_EXPERIMENTS, _build_digital_lab_html


class DigitalLabTests(unittest.TestCase):
    def test_lab_contains_seven_unique_historical_records(self):
        self.assertEqual(len(DIGITAL_LAB_EXPERIMENTS), 7)
        self.assertEqual(
            len({experiment["id"] for experiment in DIGITAL_LAB_EXPERIMENTS}),
            len(DIGITAL_LAB_EXPERIMENTS),
        )

    def test_lab_markup_contains_the_interactive_record_browser(self):
        markup = _build_digital_lab_html()

        self.assertIn("Historical acoustics experiments", markup)
        self.assertIn("experiment-selector", markup)
        self.assertIn("Hermann von Helmholtz", markup)
        self.assertIn("Manfred R. Schroeder", markup)


if __name__ == "__main__":
    unittest.main()