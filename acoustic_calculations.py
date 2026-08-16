"""Pure acoustic calculations shared by the ADA calculators."""

import math
from numbers import Real

import numpy as np
import pandas as pd


SPEED_OF_SOUND = 343.0

_AXIS_COLORS = {
    "Length": "#ef4444",
    "Width": "#22c55e",
    "Height": "#3b82f6",
}
_SBIR_FREQUENCIES = np.array(
    [40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800]
)


def _validate_room_dimensions(*dimensions):
    """Return finite positive room dimensions or raise a clear error."""
    if any(
        isinstance(dimension, bool)
        or not isinstance(dimension, Real)
        or not math.isfinite(dimension)
        or dimension <= 0
        for dimension in dimensions
    ):
        raise ValueError("Room dimensions must be finite positive numbers.")
    return tuple(float(dimension) for dimension in dimensions)


def get_room_ratios(length, width, height):
    """Return the middle/smallest and largest/smallest room-dimension ratios."""
    dimensions = sorted(
        _validate_room_dimensions(length, width, height), reverse=True
    )
    return dimensions[1] / dimensions[2], dimensions[0] / dimensions[2]


def check_bolt_area(x_ratio, y_ratio):
    """Classify ratios using ADA's simplified, exclusive Bolt-area bounds."""
    if 1.14 < x_ratio < 1.6 and 1.12 < y_ratio < 1.54:
        return "Stable Zone", "normal"
    return "Unstable", "inverse"


def calculate_modes(length, width, height, max_freq=300):
    """Calculate up to four axial modes per axis at or below ``max_freq``."""
    length, width, height = _validate_room_dimensions(length, width, height)
    modes = []
    for mode_number in range(1, 5):
        for axis, dimension in (
            ("Length", length),
            ("Width", width),
            ("Height", height),
        ):
            modes.append(
                {
                    "Freq": (SPEED_OF_SOUND / 2) * (mode_number / dimension),
                    "Axis": axis,
                    "Color": _AXIS_COLORS[axis],
                }
            )

    dataframe = pd.DataFrame(modes)
    return dataframe[dataframe["Freq"] <= max_freq].sort_values(by="Freq")


def calculate_sbir_curve(distances):
    """Return ADA's illustrative SBIR cancellation response for wall distances."""
    frequencies = _SBIR_FREQUENCIES.copy()
    response = np.zeros(len(frequencies))

    for distance in distances:
        if distance > 0:
            cancellation_frequency = SPEED_OF_SOUND / (4 * distance)
            for index, frequency in enumerate(frequencies):
                difference = abs(frequency - cancellation_frequency)
                if difference < cancellation_frequency * 0.3:
                    response[index] -= 10 * (
                        1 - difference / (cancellation_frequency * 0.3)
                    )

    return frequencies, np.maximum(response, -20)