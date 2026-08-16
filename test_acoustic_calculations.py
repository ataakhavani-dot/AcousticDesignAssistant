import unittest

import numpy as np

from acoustic_calculations import (
    SPEED_OF_SOUND,
    calculate_modes,
    calculate_sbir_curve,
    check_bolt_area,
    get_room_ratios,
)


EXPECTED_SBIR_FREQUENCIES = np.array(
    [40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800]
)


class RoomRatioTests(unittest.TestCase):
    def test_ratios_normalize_dimension_order(self):
        ratios = get_room_ratios(3.0, 5.0, 4.0)

        self.assertEqual(ratios, (4.0 / 3.0, 5.0 / 3.0))

    def test_cube_has_unity_ratios(self):
        self.assertEqual(get_room_ratios(4.0, 4.0, 4.0), (1.0, 1.0))

    def test_ratios_reject_nonphysical_dimensions(self):
        invalid_dimensions = (
            (0.0, 4.0, 3.0),
            (-1.0, 4.0, 3.0),
            (float("nan"), 4.0, 3.0),
            (float("inf"), 4.0, 3.0),
            (True, 4.0, 3.0),
        )

        for dimensions in invalid_dimensions:
            with self.subTest(dimensions=dimensions):
                with self.assertRaisesRegex(ValueError, "finite positive"):
                    get_room_ratios(*dimensions)


class BoltAreaTests(unittest.TestCase):
    def test_interior_point_is_stable(self):
        self.assertEqual(check_bolt_area(1.33, 1.50), ("Stable Zone", "normal"))

    def test_bounds_are_exclusive_and_nan_is_not_stable(self):
        outside_or_boundary_points = (
            (1.14, 1.30),
            (1.60, 1.30),
            (1.30, 1.12),
            (1.30, 1.54),
            (float("nan"), 1.30),
        )

        for point in outside_or_boundary_points:
            with self.subTest(point=point):
                self.assertEqual(check_bolt_area(*point), ("Unstable", "inverse"))


class ModalCalculationTests(unittest.TestCase):
    def test_modes_follow_axial_formula_are_colored_and_sorted(self):
        dimensions = {"Length": 5.0, "Width": 4.0, "Height": 3.0}
        colors = {"Length": "#ef4444", "Width": "#22c55e", "Height": "#3b82f6"}

        modes = calculate_modes(
            dimensions["Length"], dimensions["Width"], dimensions["Height"]
        )

        self.assertEqual(list(modes.columns), ["Freq", "Axis", "Color"])
        self.assertEqual(len(modes), 12)
        self.assertTrue(modes["Freq"].is_monotonic_increasing)
        for axis, dimension in dimensions.items():
            with self.subTest(axis=axis):
                axis_modes = modes.loc[modes["Axis"] == axis, "Freq"].to_numpy()
                expected = np.array(
                    [SPEED_OF_SOUND / 2 * mode_number / dimension for mode_number in range(1, 5)]
                )
                np.testing.assert_allclose(axis_modes, expected)
                self.assertEqual(set(modes.loc[modes["Axis"] == axis, "Color"]), {colors[axis]})

    def test_modes_include_an_exact_cutoff_and_exclude_higher_orders(self):
        dimension_at_100_hz = SPEED_OF_SOUND / (2 * 100)

        modes = calculate_modes(
            dimension_at_100_hz,
            dimension_at_100_hz,
            dimension_at_100_hz,
            max_freq=100,
        )

        self.assertEqual(len(modes), 3)
        self.assertEqual(set(modes["Axis"]), {"Length", "Width", "Height"})
        np.testing.assert_allclose(modes["Freq"].to_numpy(), [100.0, 100.0, 100.0])

    def test_modes_return_an_empty_data_frame_below_all_frequencies(self):
        modes = calculate_modes(5.0, 4.0, 3.0, max_freq=0)

        self.assertTrue(modes.empty)
        self.assertEqual(list(modes.columns), ["Freq", "Axis", "Color"])

    def test_modes_reject_nonphysical_dimensions(self):
        invalid_dimensions = (
            (0.0, 4.0, 3.0),
            (-5.0, 4.0, 3.0),
            (5.0, float("nan"), 3.0),
            (5.0, 4.0, float("inf")),
        )

        for dimensions in invalid_dimensions:
            with self.subTest(dimensions=dimensions):
                with self.assertRaisesRegex(ValueError, "finite positive"):
                    calculate_modes(*dimensions)


class SbirCalculationTests(unittest.TestCase):
    def test_sbir_uses_the_fixed_grid_and_ignores_inactive_distances(self):
        frequencies, response = calculate_sbir_curve([0.0, -0.5, float("nan"), 0.01])

        np.testing.assert_array_equal(frequencies, EXPECTED_SBIR_FREQUENCIES)
        np.testing.assert_array_equal(response, np.zeros_like(EXPECTED_SBIR_FREQUENCIES))

    def test_sbir_has_a_center_notch_with_linear_taper(self):
        distance_for_100_hz_notch = SPEED_OF_SOUND / (4 * 100)
        frequencies, response = calculate_sbir_curve([distance_for_100_hz_notch])

        response_by_frequency = dict(zip(frequencies, response))
        self.assertAlmostEqual(response_by_frequency[80], -10 * (1 - 20 / 30))
        self.assertAlmostEqual(response_by_frequency[100], -10.0)
        self.assertAlmostEqual(response_by_frequency[125], -10 * (1 - 25 / 30))
        self.assertEqual(response_by_frequency[160], 0.0)

    def test_sbir_accumulates_multiple_reflections_and_clips_at_minus_20_db(self):
        distance_for_100_hz_notch = SPEED_OF_SOUND / (4 * 100)
        frequencies, response = calculate_sbir_curve(
            [distance_for_100_hz_notch, distance_for_100_hz_notch, distance_for_100_hz_notch]
        )

        response_by_frequency = dict(zip(frequencies, response))
        self.assertEqual(response_by_frequency[100], -20.0)
        self.assertGreaterEqual(response.min(), -20.0)

    def test_sbir_returns_fresh_arrays_for_each_call(self):
        frequencies, response = calculate_sbir_curve([])
        frequencies[0] = -1
        response[0] = 1

        later_frequencies, later_response = calculate_sbir_curve([])

        self.assertEqual(later_frequencies[0], 40)
        self.assertEqual(later_response[0], 0.0)


class RoomAnalysisWorkflowTests(unittest.TestCase):
    def test_room_workflow_connects_ratios_modes_and_sbir_outputs(self):
        room = {"length": 4.5, "width": 4.0, "height": 3.0}

        ratios = get_room_ratios(room["length"], room["width"], room["height"])
        bolt_status, bolt_color = check_bolt_area(*ratios)
        modes = calculate_modes(room["length"], room["width"], room["height"])
        frequencies, response = calculate_sbir_curve([1.0, 0.8, 1.2])

        self.assertEqual((bolt_status, bolt_color), ("Stable Zone", "normal"))
        self.assertTrue((modes["Freq"] <= 300).all())
        self.assertAlmostEqual(
            modes.loc[modes["Axis"] == "Length", "Freq"].min(),
            SPEED_OF_SOUND / (2 * room["length"]),
        )
        self.assertEqual(len(frequencies), len(response))
        self.assertTrue(np.any(response < 0))


if __name__ == "__main__":
    unittest.main()