# Adding a custom I2C peripheral to a Velxio simulation

A worked example: put an **I2C EEPROM at address `0x78`** into the simulation, test it,
and remove it. `0x78` is chosen on purpose. No standard part answers there (24Cxx EEPROMs
live at `0x50`-`0x57`) and nothing on the real Waveshare board uses it, so an I2C scan
that finds `0x78` proves the peripheral was added by hand. The same steps work for any new
I2C device.

The mechanism is a Velxio **custom chip**: a small C program compiled to WebAssembly that
attaches to the I2C bus as a slave. The two source files are in
[`../custom-chips/`](../custom-chips/):

- `eeprom-0x78.chip.json` - the interface (pins `SCL`, `SDA`, `VCC`, `GND`).
- `eeprom-0x78.c` - the behavior (a 128-byte EEPROM answering only at `0x78`).

## Prerequisites

- **Self-hosted Velxio, full sim** (compile + emulate). That needs Docker + a free
  license key, see [`testing-checklist.md`](testing-checklist.md). The frontend-only
  Level 1 will not run firmware or chips.
- The custom-chip toolchain that Velxio ships (clang + WASI-SDK) and its docs:
  `docs/CUSTOM_CHIPS.md` and `docs/wiki/custom-chips-api-reference.md` in the Velxio repo.

## 1. Adding the peripheral

### 1a. Compile the chip to WebAssembly
From your Velxio checkout (same command the shipped examples use):
```bash
bash scripts/compile-chip.sh /path/to/custom-chips/eeprom-0x78.c eeprom-0x78.wasm
```

### 1b. Drop it on the canvas and wire it (UI path, simplest)
1. In the editor, open the component picker and add a **Custom Chip**.
2. Give it the `eeprom-0x78.chip.json` (interface) and the compiled program
   (`eeprom-0x78.wasm`), or paste `eeprom-0x78.c` if the UI compiles inline. See Velxio's
   `docs/CUSTOM_CHIPS.md` for the exact custom-chip loading UI.
3. Wire it to the board's I2C bus. On this board the main I2C is **SDA = GPIO11,
   SCL = GPIO10**:
   - chip `SDA` -> board `11`
   - chip `SCL` -> board `10`
   - chip `VCC` -> board `3V3`
   - chip `GND` -> board `GND`

### 1c. Or embed it in a `.vlx` project (portable path)
A custom chip travels inside a `.vlx` as a component with `metadataId: "custom-chip"`,
whose program lives in a file group keyed `group-chip-<componentId>`. Add:
```json
"components": [
  { "id": "eeprom78", "metadataId": "custom-chip", "x": 470, "y": 260, "properties": {} }
],
"fileGroups": {
  "group-chip-eeprom78": [
    { "name": "eeprom-0x78.chip.json", "content": "<the json>" },
    { "name": "chip.c",               "content": "<eeprom-0x78.c>" }
  ]
},
"wires": [
  { "id": "e-sda", "start": {"componentId":"esp32-s3","pinName":"11"}, "end": {"componentId":"eeprom78","pinName":"SDA"}, "waypoints": [], "color": "#00aaff" },
  { "id": "e-scl", "start": {"componentId":"esp32-s3","pinName":"10"}, "end": {"componentId":"eeprom78","pinName":"SCL"}, "waypoints": [], "color": "#00cc00" },
  { "id": "e-vcc", "start": {"componentId":"esp32-s3","pinName":"3V3.1"}, "end": {"componentId":"eeprom78","pinName":"VCC"}, "waypoints": [], "color": "#ff0000" },
  { "id": "e-gnd", "start": {"componentId":"esp32-s3","pinName":"GND.1"}, "end": {"componentId":"eeprom78","pinName":"GND"}, "waypoints": [], "color": "#000000" }
]
```
Then import the `.vlx` as usual (see the vlx-generator docs).

## 2. Testing it in the simulator

Velxio runs **Arduino / MicroPython / ESP-IDF**, not CircuitPython. So the in-simulator
test is **MicroPython** (near-identical to CircuitPython). Set the board's language to
MicroPython, paste this, and Run:

```python
# MicroPython - runs INSIDE the Velxio simulator
from machine import I2C, Pin
import time

i2c = I2C(0, scl=Pin(10), sda=Pin(11), freq=400000)

# 1. Scan. 0x78 should now appear (it was not there before adding the chip).
print("scan:", [hex(a) for a in i2c.scan()])

# 2. Write two bytes, then read them back.
i2c.writeto(0x78, bytes([0x00, 0xA5, 0x5A]))   # pointer=0, then data 0xA5,0x5A
time.sleep_ms(5)
i2c.writeto(0x78, bytes([0x00]))               # set pointer back to 0
data = i2c.readfrom(0x78, 2)
print("read back:", [hex(b) for b in data])    # expect ['0xa5', '0x5a']
```

**Pass criteria:** `scan:` includes `0x78`, and `read back:` is `['0xa5', '0x5a']`. That
proves the peripheral is present and its read/write round-trips.

### CircuitPython version (for the REAL board, not the sim)
Velxio cannot run CircuitPython, but here is the same test in CircuitPython for when a
real `0x78` device is on actual hardware:
```python
import board, busio, time
i2c = busio.I2C(board.SCL, board.SDA)          # or busio.I2C(board.IO10, board.IO11)
while not i2c.try_lock():
    pass
print("scan:", [hex(a) for a in i2c.scan()])
i2c.writeto(0x78, bytes([0x00, 0xA5, 0x5A]))
time.sleep(0.005)
i2c.writeto(0x78, bytes([0x00]))
buf = bytearray(2)
i2c.readfrom_into(0x78, buf)
print("read back:", [hex(b) for b in buf])
i2c.unlock()
```

## 3. Removing the peripheral

- **From the canvas (UI):** select the EEPROM chip and delete it. Deleting a component
  also drops the wires attached to it.
- **From a `.vlx`:** remove the `eeprom78` object from `components`, remove its four wires
  from `wires`, and delete the `group-chip-eeprom78` entry from `fileGroups`. Re-import.
- **Fully retire the chip:** delete `custom-chips/eeprom-0x78.chip.json`, `.c`, and the
  compiled `.wasm` if you do not want it available in the picker any more.

**Confirm removal:** re-run the MicroPython scan. `0x78` is gone from the list, and any
`i2c.writeto(0x78, ...)` now raises (no device ACKs).

## Honest notes

- This is a genuine, functioning I2C slave in the sim (reads and writes round-trip). It is
  a simplified EEPROM: 128 bytes, no write-cycle delay, no write-protect pin behavior.
- `0x78` is arbitrary and deliberately non-standard. The point is to show adding a device
  that was not there before, at an address you pick.
- Building and running custom chips needs the **full sim** (license key). I adapted this
  from Velxio's shipped, working 24C01 example, so the pattern is sound, but I have not
  run this exact chip end to end. If the scan does not find `0x78`, check the wiring
  (SDA->11, SCL->10) and that the chip compiled without errors.
