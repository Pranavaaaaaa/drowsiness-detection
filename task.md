# Driver Drowsiness Integration Tasks

## Goal

Extend DashSentinel's existing Python/MediaPipe pipeline with per-session personalized eye-closure thresholds and a time-based sustained-closure warning inspired by the browser project. Preserve DashSentinel's camera UI and ESP8266 warning/display flow.

## Tasks

- [ ] Record current behavior and run the existing scoring tests as a baseline.
- [ ] Add a robust per-eye EAR calibration using quality-valid samples where both eyes are explicitly open under the existing fixed-threshold fallback.
- [ ] Retain the configured EAR threshold as a fallback when calibration cannot gather enough valid samples.
- [ ] Detect continuous eye closure using elapsed time rather than a fixed frame count; reset timing when eyes reopen, are not visible, or the face is lost.
- [ ] Feed sustained closure into the scorer so the configured duration produces a DROWSY warning and the existing telemetry forwards that status to the ESP8266.
- [ ] Add an ESP8266-controlled active buzzer with a non-blocking intermittent beep pattern only during DROWSY; keep it silent for all other states.
- [ ] Document safe buzzer wiring through a driver stage and verify the buzzer stops when DROWSY clears.
- [ ] Expose and document the sustained-closure duration setting and calibration behavior.
- [ ] Add focused tests for per-eye calibration, fallback, closure timing, visibility/no-face resets, scoring transitions, and existing behavior.
- [ ] Run focused tests and the repository's relevant lint/build checks; manually verify the webcam and ESP serial demo when hardware is available.

## Acceptance criteria

- Startup calibration calculates separate left/right thresholds from quality-valid, visible frames where both eyes are explicitly open under the existing fallback threshold; calibration is robust to a small number of outliers.
- Insufficient/invalid calibration samples leave the prior configured threshold behavior intact and do not silently create unsafe thresholds.
- A continuous, visible two-eye closure crossing the configured duration produces a DROWSY state without depending on a particular camera FPS.
- The ESP8266 buzzer beeps intermittently only while status is DROWSY and turns off promptly for every non-DROWSY or no-data state.
- Opening either eye, losing eye visibility, losing the face, or restarting the session clears the active closure timer.
- Buzzer timing is non-blocking and does not delay serial parsing, button handling, OLED updates, or LED behavior.
- Existing alert scoring, frame-quality gates, user profile behavior, CLI defaults, and ESP8266 serial protocol remain compatible unless an explicitly documented option is selected.
- Automated tests cover the new behavior; no claim of road readiness or safety certification is introduced.

## Out of scope

- Replacing MediaPipe or adding a separate learned drowsiness classifier.
- Merging the browser app or adding a browser/backend bridge.
- PCB redesign, vehicle-control integration, production qualification, or changing the ESP8266 serial message format.
- Driving a buzzer directly from a GPIO without verifying its current draw or using a suitable driver.
- Persisting new per-eye thresholds across sessions in the first implementation; calibrate per run to keep profile migration out of scope.
