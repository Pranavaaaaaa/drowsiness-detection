---
name: drowsiness-calibration
description: "Use when implementing, reviewing, or testing DashSentinel's personalized per-eye EAR calibration, sustained eye-closure timing, DROWSY scoring, or ESP8266 warning integration."
argument-hint: "Describe the drowsiness calibration or sustained-closure change"
---

# DashSentinel Drowsiness Calibration Workflow

Use this skill for changes that adapt personalized EAR calibration and sustained eye-closure warnings into DashSentinel's Python pipeline.

## Scope

- Keep DashSentinel's Python/OpenCV/MediaPipe app as the camera-processing path.
- Preserve the existing scorer's other signals, image-quality/visibility gates, profile JSON, and ESP8266 serial protocol unless the task explicitly changes them.
- If implementing buzzer output, keep it local to ESP firmware: DROWSY-only intermittent, non-blocking, and driven through a properly rated driver stage rather than assuming GPIO current capacity.
- Treat the browser-based `driver-drowsiness-_detection` project as a behavior reference only; do not add its browser stack or copy code without a direct need.
- This is an educational warning prototype, not a certified driver-safety system. Never connect prototype outputs to vehicle controls.

## Procedure

1. Read `task.md` and `implementation-plan.md` at the repository root before coding; check whether the user has updated them.
2. Inspect current behavior in `src/features.py`, `src/app.py`, `src/scoring.py`, `src/profile.py`, `src/cli.py`, the relevant tests, and the ESP8266 serial path before editing.
3. Run the relevant existing tests first and preserve their behavior.
4. Keep the existing combined EAR feature stable for current consumers. If calibrating per eye, expose left/right EARs and use only quality-valid, visible startup-baseline samples where both eyes are explicitly open under the existing fixed-threshold fallback.
5. Use robust calibration (trimmed mean or median), guard against implausible values, and preserve the configured fixed-threshold fallback when samples are insufficient. Do not silently invent thresholds.
6. Measure sustained closure using monotonic elapsed time, not frame counts. Require both eyes visible and a usable frame; reset the timer on reopening, occlusion/poor visibility, face loss, and session reset.
7. Integrate the duration trigger with existing quality gates, score outputs, hold/recovery behavior, and `SerialTelemetry`. Keep the ESP message format unchanged unless explicitly requested.
8. If buzzer logic is in scope, use an unused verified GPIO, a compatible active buzzer and suitable driver, and a millis()-based intermittent pattern only for DROWSY; explicitly silence the buzzer on other/no-data states and do not block serial, buttons, or LEDs.
9. Add deterministic tests for calibration/fallback, timer boundaries and resets, quality gating, scorer transitions, buzzer state/timing transitions where testable, and existing regression cases. Avoid sleep-based timing tests.
10. Update relevant documentation with calibration, fallback, duration configuration, buzzer wiring, setup/testing guidance, and the educational-only safety limitation.
11. Run focused tests plus applicable lint/CI checks; if hardware is available, manually verify camera processing and ESP8266/OLED/LED/buzzer status forwarding. Report any hardware validation that could not be performed.

## Required acceptance checks

- Calibration uses reliable, neutral/open-eye samples and cannot be contaminated by drowsiness samples.
- A valid continuous bilateral eye closure crosses the configured duration independent of camera FPS.
- Eye opening, lost visibility, frame degradation, or face loss cannot leave a stale closure timer active.
- Poor-quality input cannot generate a new DROWSY trigger.
- Existing non-eye warning signals and ESP serial behavior remain intact.
- The DROWSY buzzer alert is intermittent, non-blocking, and silent outside DROWSY; its load is driven safely.
- Do not claim real-world reliability, road readiness, or certification from unit tests or a classroom demo.
