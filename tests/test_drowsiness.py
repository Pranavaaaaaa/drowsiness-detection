"""Tests for personalized eye thresholds and sustained closure scoring."""

import unittest

from src.drowsiness import SustainedEyeClosure, calibrated_eye_thresholds
from src.features import FeatureExtractor
from src.profile import DriverProfile
from src.scoring import AdaptiveScorer


class EyeCalibrationTests(unittest.TestCase):
    """Check robust per-eye threshold calculation and fallback behavior."""

    def test_uses_per_eye_medians_and_ignores_outlier(self):
        """Use separate medians so a single bad frame does not skew thresholds."""
        samples = [(0.30, 0.34)] * 30 + [(0.79, 0.79)]

        thresholds, calibrated = calibrated_eye_thresholds(samples, 0.23)

        self.assertTrue(calibrated)
        self.assertAlmostEqual(thresholds[0], 0.30 * 0.72)
        self.assertAlmostEqual(thresholds[1], 0.34 * 0.72)

    def test_insufficient_or_closed_samples_use_fallback(self):
        """Reject closed-eye samples and preserve the configured threshold."""
        thresholds, calibrated = calibrated_eye_thresholds(
            [(0.20, 0.22)] * 50,
            0.23,
        )

        self.assertFalse(calibrated)
        self.assertEqual(thresholds, (0.23, 0.23))


class SustainedEyeClosureTests(unittest.TestCase):
    """Check continuous closure time and interval reset rules."""

    def test_feature_extractor_uses_configured_duration(self):
        """Propagate non-default duration to the feature-level closure tracker."""
        extractor = FeatureExtractor(sustained_closure_seconds=2.25)

        self.assertEqual(extractor.sustained_closure.duration_seconds, 2.25)

    def test_requires_continuous_valid_bilateral_closure(self):
        """Require uninterrupted valid closure and reset on open/invalid input."""
        tracker = SustainedEyeClosure(1.5)

        self.assertEqual(tracker.update(True, True, now=10.0), 0.0)
        self.assertAlmostEqual(tracker.update(True, True, now=11.49), 1.49)
        self.assertAlmostEqual(tracker.update(True, True, now=11.5), 1.5)

        self.assertEqual(tracker.update(False, True, now=11.6), 0.0)
        self.assertEqual(tracker.update(True, True, now=12.0), 0.0)
        self.assertEqual(tracker.update(True, False, now=13.0), 0.0)

    def test_reset_clears_active_interval(self):
        """Start a fresh interval after an explicit reset."""
        tracker = SustainedEyeClosure()
        tracker.update(True, True, now=1.0)
        tracker.reset()

        self.assertEqual(tracker.update(True, True, now=4.0), 0.0)


class SustainedScoringTests(unittest.TestCase):
    """Check drowsy promotion and quality-gate interaction."""

    def test_sustained_closure_promotes_drowsy_and_finishes_calibration(self):
        """Promote immediately at the configured duration, even during warmup."""
        profile = DriverProfile("")
        scorer = AdaptiveScorer(
            profile,
            calibration_seconds=100,
            sustained_closure_seconds=1.5,
        )
        features = {
            "ear": 0.1,
            "mar": 0.05,
            "blink_rate": 15.0,
            "closed_frames_norm": 1.0,
            "closed_eye_seconds": 1.5,
            "yawn_flag": 0.0,
            "roll_deg": 0.0,
            "yaw_ratio": 0.0,
            "pitch_ratio": 0.58,
            "posture_flag": 0.0,
            "eyes_visible": 1.0,
            "mouth_visible": 1.0,
            "visibility_score": 1.0,
            "frame_usable": 1.0,
            "frame_quality": 1.0,
            "face_count": 1,
            "model_drowsy_score": None,
            "model_confidence": 0.0,
        }

        score = scorer.score(features)

        self.assertEqual(score.status, "DROWSY")
        self.assertIn("both eyes closed", score.reason)
        self.assertFalse(scorer.in_calibration())

    def test_unusable_frame_cannot_create_sustained_warning(self):
        """Keep degraded input from triggering the duration-based warning."""
        profile = DriverProfile("")
        profile.total_updates = 200
        scorer = AdaptiveScorer(
            profile,
            calibration_seconds=0,
            low_quality_hold_frames=1,
        )
        features = {
            "frame_usable": 0.0,
            "frame_quality": 0.0,
            "visibility_score": 1.0,
            "closed_eye_seconds": 10.0,
        }

        score = scorer.score(features)

        self.assertEqual(score.status, "VISION DEGRADED")


if __name__ == "__main__":
    unittest.main()
