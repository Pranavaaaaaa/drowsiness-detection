---
name: drowsiness-demo
description: "Use when preparing, setting up, rehearsing, or troubleshooting the DashSentinel educational laptop-webcam and ESP8266 drowsiness warning demo."
argument-hint: "Describe the demo setup, rehearsal, or troubleshooting need"
---

# DashSentinel Educational Demo Workflow

Use this skill to prepare, operate, rehearse, or troubleshoot the DashSentinel demo on a Windows laptop with an optional ESP8266 alert display.

## Read first

1. Read `docs/demo/task.md` and `docs/demo/implementation-plan.md`; respect user edits.
2. Check the root `task.md` and `implementation-plan.md` before claiming personalized EAR calibration or sustained-closure timing has been implemented.
3. Inspect the actual CLI options, firmware pin assignments, and current tests when giving commands or troubleshooting. Do not assume planned features are already available.

## Operating model

- The laptop's Python process owns the webcam, MediaPipe inference, scoring, and serial output.
- The ESP8266 runs separately compiled/uploaded firmware and only renders telemetry/LED state and relays button commands.
- The ESP does not run Python or MediaPipe. Do not run the browser-based reference app in parallel against the same camera.
- The KiCad PCB is optional; the circuit may be built on a breadboard using firmware pins.
- A separate ONNX classifier is not required for the demo.

## Workflow

1. Confirm the educational warning-only scope and stationary demo conditions.
2. Check for Python, webcam, PlatformIO/firmware prerequisites, and optional ESP/OLED/LED/button components.
3. First prepare and test the camera-only Python app from the DashSentinel repository root.
4. Then assemble the breadboard and build/upload the ESP firmware from `DisplayModule`, checking the actual board pinout and safe 3.3 V logic.
5. Identify the actual Windows COM port and close all other serial monitors before the Python app opens it.
6. Run the app with the current supported CLI flags; verify camera, baseline, display status, LEDs, and recovery in a stationary rehearsal.
7. Test no-face/poor-visibility handling and buttons without claiming a vision failure means the driver is alert.
8. Maintain a UI-only fallback and label any screenshots/recordings as backup, not live measurements.
9. Troubleshoot one interface at a time: camera-only first, then board firmware/OLED, then serial connection.
10. Report exactly what was tested, what requires the user's hardware, and any features that remain planned rather than implemented.

## Wiring reference

Use the checked-in firmware in `DisplayModule/src/main.cpp` as the source of truth:

- OLED SDA=D2, SCL=D1, VCC=3V3, GND=GND.
- Baseline reset button: D3 to GND; stats reset button: D4 to GND (firmware uses internal pull-ups).
- Red/green/yellow LEDs: D5/D6/D7 respectively, each in series with its own current-limiting resistor and returning to GND.
- Optional DROWSY buzzer: use D0 (GPIO16) as control only after checking the board variant; use a 3.3 V-compatible active buzzer through a properly rated driver stage, with shared ground. Expect intermittent beeps only while DROWSY once that firmware change is implemented.
- Avoid pressing D3/D4 during power-up/reset because these are boot-sensitive ESP8266 pins.

## Required safety boundaries

- Never connect the prototype to ignition, steering, braking, or other vehicle controls.
- Do not induce eye closure while driving; rehearse seated and stationary.
- Do not claim road readiness, certification, or general accuracy from a classroom demo.
- Minimize camera data retention and obtain consent before recording participants.
