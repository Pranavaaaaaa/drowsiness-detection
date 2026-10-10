"""Small, dependency-free helpers for personalized eye closure detection."""

import math
import time


def calibrated_eye_thresholds(
    samples,
    fallback_threshold,
    calibration_factor=0.72,
    min_samples=30,
):
    """Return robust per-eye thresholds, or the configured fallback pair."""
    fallback = float(fallback_threshold)
    fallback_pair = (fallback, fallback)
    if len(samples) < min_samples:
        return fallback_pair, False

    left_values = []
    right_values = []
    for left, right in samples:
        left = float(left)
        right = float(right)
        if not (
            math.isfinite(left)
            and math.isfinite(right)
            and 0.05 <= left <= 0.8
            and 0.05 <= right <= 0.8
            and left > fallback
            and right > fallback
        ):
            continue
        left_values.append(left)
        right_values.append(right)

    if len(left_values) < min_samples:
        return fallback_pair, False

    factor = float(calibration_factor)
    if not math.isfinite(factor) or not 0.3 <= factor <= 0.95:
        return fallback_pair, False

    left_threshold = _median(left_values) * factor
    right_threshold = _median(right_values) * factor
    if not all(math.isfinite(value) and 0.05 <= value <= 0.5
               for value in (left_threshold, right_threshold)):
        return fallback_pair, False

    return (left_threshold, right_threshold), True


def _median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


class SustainedEyeClosure:
    """Track uninterrupted, valid bilateral eye closure using monotonic time."""

    def __init__(self, duration_seconds=1.5):
        self.duration_seconds = float(duration_seconds)
        self.closed_since = None

    def reset(self):
        """Clear the active closure interval."""
        self.closed_since = None

    def update(self, both_eyes_closed, valid, now=None):
        """Return elapsed closure seconds; invalid/open input clears the timer."""
        if not both_eyes_closed or not valid:
            self.reset()
            return 0.0

        current_time = time.monotonic() if now is None else float(now)
        if self.closed_since is None:
            self.closed_since = current_time
        return max(0.0, current_time - self.closed_since)
