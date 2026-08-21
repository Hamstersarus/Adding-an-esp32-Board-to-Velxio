# vlx-generator: custom-board test files for Velxio

Generate an importable Velxio `.vlx` project from a small `board-spec.json`, so you can
compile and run firmware for a **custom board before the hardware exists**. The `.vlx`
models the board as an MCU plus interface parts wired to a **custom pinout**; you import
it into Velxio, load your firmware, and run it against that wiring.

This is a cleaner method than patching Velxio's source (see the repo's other docs): no
rebuild, no license key, just a file you import via **File -> Open project**.

## Usage

```bash
python3 gen_vlx.py examples/waveshare-esp32-s3-touch-lcd-2.8/board-spec.json
# -> writes waveshare-esp32-s3-touch-lcd-2.8.vlx next to the spec
```
Then in Velxio: **File -> Open project** -> pick the `.vlx`. Hit Run.

## Spec format (`board-spec.json`)

```json
{
  "name": "My Custom Board",
  "boardKind": "esp32-s3",
  "firmware": "sketch.ino",
  "libraries": ["Adafruit ILI9341"],
  "interfaces": [
    { "id": "tft1", "part": "ili9341" }
  ],
  "pinout": [
    { "gpio": "45", "to": "tft1:MOSI" },
    { "gpio": "GND.1", "to": "tft1:GND" }
  ]
}
```

| Field | Meaning |
|---|---|
| `boardKind` | The MCU. Any Velxio board id (`esp32-s3`, `esp32`, `esp32-c3`, ...). |
| `firmware` | Path to your `.ino` (relative to the spec). Or inline `"code": "..."`. |
| `libraries` | Optional Arduino libraries to declare so the sketch compiles. |
| `interfaces` | The peripherals. `id` is your name; `part` is a Velxio component. |
| `pinout` | **The wiring.** `gpio` is a board pin, `to` is `"interfaceId:pinName"`. Optional `color`. |

## The rules that make it import cleanly

1. **File group key must be `group-<boardId>`.** The generator sets the board id to
   `boardKind` and the group to `group-<boardKind>`. Get this wrong and the sketch does
   not attach (you get a `libraries.json`-only project and "no firmware").
2. **`part` = the Velxio/Wokwi component id with the `wokwi-`/`velxio-` prefix stripped.**
   `ili9341`, `ssd1306-i2c-4pin`, `led`, `hc-sr04`, ... The generator strips the prefix
   for you, so `"ili9341"` and `"wokwi-ili9341"` both work.
3. **Board pins are GPIO numbers as strings** (`"45"`), plus named power pins
   (`"3V3.1"`, `"3V3.2"`, `"5V"`, `"GND.1"`..`"GND.4"`). Component pins use the part's
   own names (`MOSI`, `SCK`, `CS`, `D/C`, `RST`, `LED`, `VCC`, `GND`, ...).

## Finding part names and pin names

- **Parts:** open the component picker in Velxio, or grep the source
  (`frontend/src/data/examples*.ts` shows real part types and their pin names).
- **Board pins:** the ESP32-S3 exposes GPIO 0-21, 35-42, 45-48 plus 3V3/5V/GND. Other
  MCUs expose their own set.

## Honest limits

- The firmware genuinely runs on the emulated MCU and its pin I/O is real, but an
  interface only **responds** if Velxio has a model for it. Standard parts (SPI/I2C
  displays, buttons, common sensors) work; a bespoke interface needs a **custom chip**
  (C compiled to WASM, see Velxio's `docs/CUSTOM_CHIPS.md`).
- Pick the closest available part. Example: the Waveshare board's ST7789 is modeled with
  `ili9341` (a near-identical SPI TFT); its CST3530 touch has no part and is omitted.
- ESP32 boards import via `.vlx` only. The Wokwi `.zip` importer does not map ESP32
  boards (it defaults them to Arduino Uno).

## Verified

The included Waveshare example imports into self-hosted Velxio, compiles, and runs on the
emulated ESP32-S3 (the sketch draws to the TFT and prints `drawn` on serial).
