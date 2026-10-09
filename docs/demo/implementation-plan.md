# Demo Plan: Laptop Webcam and ESP8266 Warning Display

## Objective

Prepare and rehearse a dependable classroom demo using DashSentinel's existing Python/OpenCV/MediaPipe pipeline, laptop webcam, and ESP8266 serial display. The separate browser project is not part of the live execution path. The KiCad carrier board is optional; assemble the existing circuit on a breadboard.

## Prerequisite

The proposed per-eye EAR calibration and time-based sustained-eye-closure logic is tracked separately in the repository-root `task.md` and `implementation-plan.md`. Do not claim the personalized thresholds or configured sustained-closure duration as delivered until that integration is implemented, tested, and present in the executable Python app.

## Hardware checklist

Required for camera-only UI:

- Windows laptop with Python and a working built-in or USB webcam.

Add the hardware alert interface:

- NodeMCU ESP8266 / ESP-12E board and USB data cable.
- SSD1306 I2C OLED, 128x64.
- Breadboard and jumper wires.
- Two momentary push buttons.
- Red, yellow, and green LEDs.
- Three 330-ohm series resistors, one per LED.
- A 3.3 V-compatible active buzzer module plus a suitable transistor/driver and base/gate resistor; do not assume the ESP8266 GPIO can directly supply buzzer current.

No KiCad fabrication is required. The code pin assignments in `DisplayModule/src/main.cpp` are:

| Module | NodeMCU connection |
| --- | --- |
| OLED SDA | D2 |
| OLED SCL | D1 |
| OLED VCC / GND | 3V3 / GND |
| Baseline-reset button | D3 to GND |
| Stats-reset button | D4 to GND |
| Red LED | D5 -> 330-ohm resistor -> LED anode; cathode -> GND |
| Green LED | D6 -> 330-ohm resistor -> LED anode; cathode -> GND |
| Yellow LED | D7 -> 330-ohm resistor -> LED anode; cathode -> GND |
| Active buzzer control | D0 (GPIO16) -> suitable driver input; driver switches buzzer current; share GND |

Use ESP8266 3.3 V GPIO logic; never apply 5 V to its GPIO pins. D3 and D4 are boot-strapping pins: do not hold either button while powering or resetting the board. Check the OLED and buzzer module voltage requirements. Power the buzzer from a suitable supply through the driver stage, not directly from the GPIO.

## Software setup (Windows)

Run from the DashSentinel repository root in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, use the environment's Python executable directly or activate it using the local machine's approved policy; do not change machine-wide execution policy just for this demo.

### Test Python and camera before hardware

```powershell
python run_dashsentinel.py --show-ui --draw-landmarks
```

Allow the startup baseline to collect valid samples. Confirm the webcam image and landmark overlay appear, then close with `q`. If camera 0 is not the intended camera, use the CLI's `--camera` option (for example `--camera 1`).

### Build and upload ESP firmware

- Open `DisplayModule` in VS Code with PlatformIO installed.
- Select the ESP8266/ESP-12E environment from `DisplayModule/platformio.ini`.
- Build and upload to the board using PlatformIO. Record the assigned Windows COM port from Device Manager.
- Confirm the OLED shows its startup/waiting message.
- Close PlatformIO's serial monitor before starting Python because both programs cannot own the same COM port simultaneously.

### Run the combined demo

Replace `COM3` with the actual board port:

```powershell
python run_dashsentinel.py --show-ui --draw-landmarks --enable-esp-serial --esp-port COM3
```

Python performs camera inference and scoring. The ESP8266 receives status/score telemetry over USB serial; it does not run MediaPipe or the Python detection algorithm.

## Rehearsal sequence

1. **Startup:** Show camera acquisition and baseline/calibration instructions; maintain a neutral open-eye posture until the app reports active operation.
2. **Normal attentive state:** Confirm the UI shows the current state and the OLED/green LED reflects ALERT.
3. **Short blink:** Demonstrate that a brief blink should not be presented as a sustained-closure event.
4. **Sustained eye closure:** After the new duration feature has been implemented, close both eyes while seated and stationary for longer than the configured threshold. Confirm the Python state and ESP OLED/red LED plus intermittent buzzer warn, then confirm the buzzer silences and the warning recovers after reopening. Do not perform this while driving or operating a moving vehicle.
5. **Poor visibility / no face:** Briefly move out of frame or obscure the face and explain the no-face/vision-degraded indication. Do not interpret it as ALERT or proof of safe driving.
6. **Buttons:** If included, press baseline reset and stats reset separately; explain what each does and observe Python's response.
7. **Shutdown:** Press `q` to stop Python, then disconnect the board after the serial connection closes.

Existing frame processing, scores, and status transitions may change with camera placement, room lighting, glasses, and the user. Rehearse in the same setup as the presentation and do not claim this small demonstration validates general accuracy.

## Pre-demo verification and fallbacks

- Charge/connect laptop power and keep the webcam unobstructed.
- Check the COM port, USB data cable, OLED wiring, common ground, LED polarity, and series resistors.
- Ensure PlatformIO's serial monitor is closed before launching Python.
- Keep a known-good UI-only command ready if the ESP, cable, or COM port fails.
- Keep clearly labeled screenshots or a recording as backup evidence, but identify them as recorded material rather than a live test.
- Do not install or configure a separate ONNX classifier solely for the demo; it is optional.

## Safety and privacy notes

- Demonstrate while seated at a stationary desk or safe stationary mock-up only.
- Do not connect the prototype to vehicle controls or use it to decide whether it is safe to drive.
- Do not record or retain classmates' camera footage without their consent. Prefer live processing and avoid unnecessary logs.
- Describe the app as an educational warning prototype, not a certified or validated driver monitoring system.

## Completion criteria

The demo is ready when the camera-only path and hardware path have each been rehearsed, the serial alert/recovery behavior has been observed (or a clear UI-only fallback is prepared), and every feature claimed during presentation matches the implemented and tested repository behavior.
