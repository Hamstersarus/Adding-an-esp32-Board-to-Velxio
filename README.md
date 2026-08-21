# Velxio board support: Waveshare ESP32-S3-Touch-LCD-2.8

Everything needed to add the **Waveshare ESP32-S3-Touch-LCD-2.8** board to the
open-source [Velxio](https://github.com/davidmonterocrespo24/velxio) browser-based
ESP32 simulator, plus a **reusable guide** for adding *any* ESP32 board to Velxio.

## Contents

| File | What it is |
|---|---|
| [`docs/adding-an-esp32-board-to-velxio.md`](docs/adding-an-esp32-board-to-velxio.md) | **The reusable guide.** Add any ESP32 board to Velxio. Start here for future boards. |
| [`docs/testing-checklist.md`](docs/testing-checklist.md) | **What you need to fully test it yourself** (Level 1 frontend + Level 2 compile/boot). |
| [`board-profile.md`](board-profile.md) | This board's specs + fully verified pinout + Velxio settings. |
| [`velxio-patch/patch_velxio.py`](velxio-patch/patch_velxio.py) | Script that applies the board edits to a Velxio checkout. |
| [`velxio-patch/CHANGES.md`](velxio-patch/CHANGES.md) | The exact edits, spelled out, for hand-application or review. |
| [`velxio-patch/pin-map.ts`](velxio-patch/pin-map.ts) | Pin-map snippet (label -> GPIO). |

## Reproduce it yourself, start to finish

```bash
# 1. get Velxio
git clone https://github.com/davidmonterocrespo24/velxio && cd velxio
# 2. apply the board
python3 /path/to/this-repo/velxio-patch/patch_velxio.py "$PWD"
# 3a. Level 1: see it in the picker (no account)
cd frontend && npm install && ./node_modules/.bin/vite --host   # -> localhost:5173
# 3b. Level 2: compile + boot it (needs a free key from velxio.dev/license/signup)
#   cd .. && docker compose build --build-arg VELXIO_LICENSE_KEY=vlx_personal_... && docker compose up -d
```
Full checklist and gotchas: `docs/testing-checklist.md`.

## Why the pinout is trustworthy

Verified on real hardware during a CircuitPython bring-up: LCD/SD/touch pins read from the
board's CircuitPython `board` module, and the touch controller identified by I²C scan as a
**CST3530 at `0x58`** (Waveshare's docs mislabel it CST328 @ `0x1A`). See `board-profile.md`.
