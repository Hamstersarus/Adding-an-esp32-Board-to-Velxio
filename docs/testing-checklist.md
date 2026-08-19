# What you need to fully test the board in Velxio

Two levels of testing, because Velxio splits into a frontend (board UI) and a backend
(compile + QEMU emulation). The backend's emulator binaries are gated behind a free key.

## Prerequisites

| Need | For | Notes |
|---|---|---|
| **Node 20 + npm** | Frontend (Level 1) | `node --version` should be v20.x |
| **Docker + `docker compose` v2** | Full sim (Level 2) | `sudo apt install docker-compose-v2` if `docker compose version` fails |
| **A free Velxio license key** | Full sim (Level 2) | Sign up at <https://velxio.dev/license/signup>. Gates the QEMU `.so` download. Without it the Docker build fails at the `qemu-provider` step. |

## Level 1: Frontend appearance (no account, no key)

Confirms the board is correctly *defined*: appears in the picker, right label/description/
visual, right default options, right pinout labels.

```bash
cd velxio/frontend
npm install
# NOTE: `npm run dev` runs a codegen step that needs the root `typescript` dep,
# which a frontend-only install does not provide. Run vite directly instead
# (the generated files are already committed):
./node_modules/.bin/vite --host
```
Open <http://localhost:5173>. **Test checklist:**
- [ ] "Waveshare ESP32-S3 Touch LCD 2.8" appears in the add-board picker
- [ ] Its tile shows the ESP32-S3 DevKit visual + your description
- [ ] Selecting it puts the board on the canvas
- [ ] Board options default to **Flash 16 MB** and **PSRAM OPI**
- [ ] Pin labels on the board are the ESP32-S3 GPIOs

Level 1 does **not** compile or emulate (no backend). That is expected.

## Level 2: Compile + emulate (needs Docker + free key)

Confirms the board actually **compiles firmware and boots in QEMU**.

```bash
cd velxio
# one-time: get a free key at velxio.dev/license/signup -> vlx_personal_...
docker compose build --build-arg VELXIO_LICENSE_KEY=vlx_personal_XXXX
docker compose up -d
```
First build is ~10 to 15 min (downloads ESP-IDF, builds frontend). Open
<http://localhost:3080>. **Test checklist:**
- [ ] Everything from Level 1 (the picker/options/visual)
- [ ] Load a blink or `Serial.println` sketch, press **Run**
- [ ] OUTPUT shows "Compilation successful" for `esp32:esp32:esp32s3`
- [ ] Serial monitor shows the ESP32-S3 ROM boot banner, then your prints
      (remember `Serial.begin(115200);` in `setup()`)

## What you canNOT test (honest limits)

The board's actual peripherals are **not** simulated at any level:
- ST7789 display, CST3530 touch, QMI8658 IMU, PCF85063 RTC, PCM5101 audio.

QEMU emulates the ESP32-S3 SoC (CPU, GPIO, SPI/I²C controllers), not the specific chips
soldered to the board. A generic TFT component *might* render if wired by hand; the rest
would each need a custom-chip model (see the main guide). So "fully tested" here means:
**correct board identity + CPU-accurate compile and boot**, not a working touchscreen.
