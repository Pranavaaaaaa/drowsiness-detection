# Implementation Plan: Personalized Eye Closure and Sustained-Warning Logic

## Objective

Reuse DashSentinel for the laptop-webcam and ESP8266 prototype while adapting two useful ideas from `driver-drowsiness-_detection`: user-specific eye calibration and a warning after sustained eye closure. Add a local ESP8266 buzzer alert for the DROWSY status. The browser app is a reference for behavior, not a code dependency. Keep video inference in the existing Python/MediaPipe pipeline and use its existing serial telemetry to drive the OLED, LEDs, and buzzer.

## Current state

- `src/app.py` already performs a startup baseline and accepts only frames that pass quality, visibility, and pose checks.
- `src/features.py` computes smoothed EAR and has a fixed `--ear-threshold`; it already tracks closed-eye frames, but this is frame-count based and decays on open frames.
- `src/profile.py` persists aggregate feature statistics, including mean EAR, but does not store left/right eye thresholds.
- `src/scoring.py` combines eye closure with blink, yawn, pose, optional-model, and quality signals, then applies smoothing and status hysteresis.
- The existing ESP8266 serial protocol sends status, attentiveness, and drowsy score; `DisplayModule/src/main.cpp` maps DROWSY to the red LED and OLED.
- Current ESP8266 pin assignments use D1-D7; D0 is unused and can be reserved for buzzer control after confirming the specific board/module.

## Decisions

- Calibrate left and right eyes separately from the already-existing startup baseline; use only valid, visible, stable open-eye samples.
- Compute a robust center per eye (trimmed mean or median), then multiply by a configurable calibration factor. Start with `0.72` to match the reference app, but retain a floor/ceiling and test against the project's existing fixed threshold to avoid zero or implausible thresholds.
- Keep calibration per session in the first implementation. Do not change the persisted profile JSON schema; if calibration samples are insufficient, use the current configured EAR threshold.
- Measure closure with monotonic elapsed seconds, not frame counts. Use a configurable default duration of `1.5` seconds, matching the reference app.
- Only count closure while both eye groups are visible and the frame is usable. Clear the timer on reopen, invalid eye visibility, loss of face, or feature reset.
- When valid continuous closure reaches the duration, have scoring promote to DROWSY while respecting the existing quality gate and recovery/hysteresis behavior. Preserve all other scoring signals and the ESP serial wire format.
- Add a 3.3 V-compatible active buzzer driven from the ESP8266 through an appropriate transistor/driver stage; use the currently unused D0 pin as the control signal, subject to the actual board pinout. Never drive a buzzer load directly from a GPIO unless its current is verified within the pin's safe limits.
- Generate a non-blocking intermittent beep pattern only while received status is DROWSY. Silence it for every other status and on startup/no data. Use millis()-based timing so serial reads, OLED refreshes, LED patterns, and button handling remain responsive.
- Keep the existing desktop OpenCV display. No browser merge, ONNX model, board redesign, or vehicle-control integration in this scope.

## Implementation sequence

### 1. Baseline and regression inventory

- Run the current focused tests in `tests/test_scoring_quality.py`.
- Record the active CLI settings and existing quality/scoring behavior before changing the threshold/time logic.
- Use this repository as the implementation root; consult the separate browser repository only for the intended calibration and duration behavior.

### 2. Extend feature extraction

Target: `src/features.py`

- Calculate and expose separate `left_ear` and `right_ear` values while preserving the existing combined `ear` field used by the profile and scorer.
- Add explicit per-eye threshold state and a method to set calibrated thresholds safely; initialize both thresholds from the existing `ear_threshold` option.
- Use per-eye comparisons for closure detection, requiring both eyes to be below their thresholds for the sustained-drowsiness timer.
- Track the start of uninterrupted bilateral closure with `time.monotonic()`, and emit duration/prolonged-closure feature values.
- Reset the timer when either eye opens, visibility is invalid, or `reset()` is called. Keep extractor resets from accidentally discarding successfully calibrated thresholds during the handoff from baseline to active mode.
- Preserve the existing blink and closed-frame features to avoid changing unrelated scoring behavior.

### 3. Calibrate during the existing startup baseline

Target: `src/app.py`, and `src/cli.py` if adding a user-facing calibration factor.

- During `_run_startup_baseline`, collect left/right EAR samples only after `_feature_is_valid_for_baseline(features)` succeeds and both eyes' EAR values exceed the current fixed fallback threshold. This prevents closed or borderline samples from lowering the personalized open-eye baseline.
- Exclude implausible values and use a robust statistic so occasional landmark outliers do not dominate the calibration.
- Apply calibration once baseline collection ends and before active scoring begins; do not use closed-eye samples to update the baseline.
- If there are too few usable per-eye samples, retain the fixed threshold from `--ear-threshold` and show/print a clear fallback notice.
- Add an optional CLI setting for the calibration factor only if it is useful for controlled demonstrations; otherwise use the documented default to keep the CLI small.
- Update the startup overlay or status text to indicate calibration progress and whether calibrated thresholds or fallback thresholds are active.

### 4. Integrate sustained closure with scoring and hardware alerts

Target: `src/scoring.py`, `src/cli.py`, `src/app.py`, and `DisplayModule/src/main.cpp`.

- Add a duration option (default `1.5` seconds) and pass it consistently to the extractor/scorer.
- Keep the existing quality gate first: degraded or occluded frames cannot create a new sustained-closure trigger.
- When valid `closed_eye_seconds` reaches the configured duration, select DROWSY as the desired state and include an explanatory reason, while retaining state hold/recovery behavior when eyes reopen.
- Ensure the `ScoreOutput.status` continues through the existing `SerialTelemetry.send()` path; do not alter the comma-separated ESP protocol.
- Define a buzzer control output on D0 in the ESP firmware. Drive a 3.3 V-compatible active buzzer module through a suitable transistor/driver circuit rather than assuming a GPIO can supply the buzzer current.
- Add a non-blocking intermittent beep pattern while `currentStatus == "DROWSY"`; ensure buzzer output is inactive for ALERT, WARNING, LEARNING BASELINE, NO FACE, VISION DEGRADED, invalid/no data, and immediately when leaving DROWSY.
- Keep buzzer state changes synchronized with serial status parsing, and avoid delay-based patterns that block serial/button/LED processing. Preserve the existing serial message format.
- Display current closure duration and selected threshold(s) in the desktop overlay for demonstration/debugging if that fits without clutter.

### 5. Tests and documentation

Target: `tests/`, `README.md`, and relevant safety/model docs only if behavior descriptions need correction.

- Add deterministic tests for robust per-eye calibration, invalid/insufficient-sample fallback, and threshold bounds.
- Add timing tests with controlled monotonic timestamps or a narrow clock-injection seam; cover threshold just below/at/above the duration without sleeping.
- Verify timer reset on eye opening, low visibility, no face, and extractor reset.
- Verify the scorer marks a valid sustained closure as DROWSY, does not promote on an unusable frame, and recovers after the event using existing status rules.
- Verify buzzer is silent for all non-DROWSY states, beeps intermittently while DROWSY, stops promptly when status leaves DROWSY, and does not block serial parsing or button response.
- Keep and run the pre-existing scoring/quality tests.
- Document that the app calibrates during startup, the duration option/default, fallback behavior, buzzer hardware/driver wiring, and that the prototype is educational—not a validated driver safety system.

### 6. Validate the integrated demo

- Run focused automated tests and the repository's lint/CI-equivalent checks that cover touched Python files.
- Build the PlatformIO firmware and test the buzzer control/status transitions with the actual compatible buzzer and driver stage when hardware is available.
- Run the Python camera demo without hardware first; test open eyes, deliberate short blinks, and a sustained eye closure under stable lighting.
- If the ESP8266 is available, flash the updated firmware and verify status forwarding over the selected COM port: normal state, DROWSY/red LED/intermittent buzzer, silence and recovery.
- Record observed limitations rather than inferring real-world accuracy from a successful software test.

## Likely files

- Modify: `src/features.py`, `src/app.py`, `src/scoring.py`, `src/cli.py`, `DisplayModule/src/main.cpp`
- Tests: add focused tests under `tests/`; retain `tests/test_scoring_quality.py`
- Documentation: update `README.md` and, only as needed, `docs/PRODUCT_SAFETY.md`
- Keep unchanged: ESP8266 serial protocol; firmware changes are limited to local buzzer control alongside current display/LED behavior

## Risks and mitigations

- **Calibration contains closed-eye samples:** accept samples only from quality/visibility-valid frames where both eyes are explicitly open under the fixed fallback threshold; robustly trim outliers and fall back if sample count is low.
- **Different face geometry or camera rates:** calibrate per eye, use monotonic elapsed time, and verify duration behavior at multiple processing rates.
- **Occlusion mistaken for closure:** gate on eye visibility and usable-frame status, and clear timing when these gates fail.
- **Existing state smoothing delays warning:** ensure the sustained-duration path can request DROWSY while keeping the quality gate and recovery hysteresis; test the exact threshold transition.
- **ESP8266 GPIO overcurrent or boot instability:** use D0 only after confirming the board pinout, drive the buzzer through a properly rated transistor/driver, keep grounds common, and avoid using boot-strapping pins for the buzzer.
- **Audio alert blocks embedded loop:** implement beep cadence with elapsed-time checks rather than `delay()`, and force the buzzer inactive on every non-DROWSY status.
- **Prototype mistaken for a safety product:** retain the educational warning-only disclaimer and never connect alerts to vehicle controls.

## Completion criteria

Implementation is complete when every acceptance criterion in `task.md` is met, focused tests pass, existing scoring tests remain green, and the camera-to-ESP warning path is manually exercised when the hardware is available.
