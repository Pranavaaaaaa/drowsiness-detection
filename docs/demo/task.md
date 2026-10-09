# DashSentinel Demo Preparation Tasks

## Goal

Prepare a repeatable educational demonstration of DashSentinel's laptop webcam detection and ESP8266 warning display. Use the Python application as the camera/scoring system and the ESP8266 as a serial-connected OLED/LED alert module. Do not fabricate the KiCad board.

## Tasks

- [ ] Confirm the drowsiness calibration/sustained-closure integration in the root `task.md` is implemented and its tests pass before presenting those features as available.
- [ ] Assemble the ESP8266, OLED, LEDs with series resistors, buttons, breadboard, and jumper wires according to `DisplayModule/src/main.cpp`.
- [ ] Add the active buzzer and suitable driver stage on the planned free ESP8266 control pin; verify the buzzer beeps intermittently only during DROWSY and is silent otherwise.
- [ ] Install Python requirements and run the camera UI without ESP hardware first.
- [ ] Build and upload `DisplayModule` firmware; identify the board's COM port and ensure no other serial monitor holds it open.
- [ ] Run the camera app with the correct camera index and ESP COM port; verify live serial status appears on OLED and LEDs.
- [ ] Rehearse normal/alert, calibration, sustained eye-closure warning with intermittent buzzer, recovery/silence, face-loss/poor-visibility behavior, and button actions.
- [ ] Prepare a backup plan (UI-only run, saved screenshots/video, spare USB cable, and the Python command/COM port written down) without presenting saved media as live inference.
- [ ] Present the prototype as an educational warning system and state its limitations; do not test it while driving or connect it to vehicle controls.

## Acceptance criteria

- The laptop can access the webcam and the Python app reaches its active state without an ONNX classifier.
- The ESP firmware is uploaded and the OLED receives telemetry when Python opens the correct COM port.
- Expected ALERT/WARNING/DROWSY transitions are visible in the Python UI and appropriate OLED/LED indication is observed, including recovery.
- Button commands work if the hardware/button wiring is included in the demo.
- Loss of face or unusable lighting is described as an unreliable-input condition, not as proof the driver is alert.
- The demo can be run from a cleanly documented sequence with a UI-only fallback if hardware or serial communication fails.
- No road-safety, certification, or production-readiness claim is made.

## Out of scope

- PCB fabrication or redesign.
- Connecting to a vehicle, controlling ignition, steering, braking, or any other safety-critical system.
- A browser frontend, cloud service, required separate drowsiness classifier, or retraining a model.
- Claiming real-world accuracy from a classroom demonstration.
