# PR: add `waveshare-esp32-s3-touch-lcd-2.8` to Velxio

The exact source edits, **verified by applying them to a real Velxio checkout** and
running the frontend (the board appeared in the picker with the right label, description,
ESP32-S3 visual, and 16MB/OPI options). All under `frontend/src/`.

The fastest way to apply them is the script:
```bash
python3 patch_velxio.py /path/to/velxio
```
It inserts each entry after its map/set declaration and self-reports. What it does, spelled
out (in case an anchor moves and you apply by hand):

## `types/board.ts`
```ts
// BoardKind union (add a member):
  | 'waveshare-esp32-s3-touch-lcd-2.8' // Waveshare 2.8" touch LCD (N16R8), QEMU (esp32-s3)
// BOARD_SUPPORTS_MICROPYTHON set, BOARD_SUPPORTS_ESPIDF set (add to each):
  'waveshare-esp32-s3-touch-lcd-2.8',
// BOARD_KIND_LABELS:
  'waveshare-esp32-s3-touch-lcd-2.8': 'Waveshare ESP32-S3 Touch LCD 2.8',
// BOARD_KIND_FQBN (generic S3 Dev Module target):
  'waveshare-esp32-s3-touch-lcd-2.8': 'esp32:esp32:esp32s3',
```

## `components/ComponentPickerModal.tsx`
```ts
// ALL_BOARDS  <-- this is what makes the tile appear in the picker
  'waveshare-esp32-s3-touch-lcd-2.8',
// BOARD_DESCRIPTIONS:
  'waveshare-esp32-s3-touch-lcd-2.8': 'Waveshare 2.8" touch LCD: ESP32-S3 N16R8, ST7789 + CST3530',
// BOARD_TAG:
  'waveshare-esp32-s3-touch-lcd-2.8': 'ESP32-S3',
```

## `types/boardOptions.ts`
```ts
// ESP32_S3_KINDS set (routes/treats it as an S3):
  'waveshare-esp32-s3-touch-lcd-2.8',
// inside getDefaultOptionsForKind(), after `const defaults = { ...DEFAULT_ESP32_OPTIONS };`:
  if (kind === 'waveshare-esp32-s3-touch-lcd-2.8') { defaults.flashSize = '16MB'; defaults.psram = 'opi'; }
```

## `components/velxio-components/Esp32Element.ts`
```ts
// reuse the ESP32-S3 DevKit skin + pins:
  'waveshare-esp32-s3-touch-lcd-2.8': { svgUrl: esp32S3SvgUrl, w: 128, h: 350, pins: PINS_ESP32_S3 },
```

## `utils/boardPinMapping.ts`
```ts
// BOARD_COMPONENT_IDS:
  'waveshare-esp32-s3-touch-lcd-2.8',
```

## Before a production build / PR: the exhaustive maps

The above is enough for **`vite` dev** (Level 1 testing), which does not typecheck. For
`tsc` / `vite build` / the Docker image to succeed, every `Record<BoardKind, ...>` must
include the id. See the RECOMMENDED section of `../docs/adding-an-esp32-board-to-velxio.md`
for the remaining cosmetic maps (`EditorToolbar`, `FileExplorer`, `BoardPickerModal`) and
the hard-coded `=== 'esp32-s3'` behavior checks.

## Reviewer reality check

Makes the board **selectable, CPU-accurate (S3 / 16MB / OPI), correctly pinned-out**. Adds
**no** peripheral emulation: the ST7789/CST3530/IMU/RTC/audio are not modeled.
