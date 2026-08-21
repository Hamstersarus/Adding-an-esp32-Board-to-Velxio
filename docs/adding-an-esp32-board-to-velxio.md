# How to add an ESP32 board on Velxio

A reusable recipe for adding a new ESP32-family board to
[Velxio](https://github.com/davidmonterocrespo24/velxio). Verified by actually doing it
against a real checkout (fetched 2026-08). Line numbers drift; search for the symbols.

## Something that makes adding a board easy

**The QEMU backend only knows chip *families*, not board variants.** In
`backend/app/services/esp_qemu_manager.py`:

```python
'esp32-s3': (QEMU_XTENSA, 'esp32s3'),   # -> qemu-system-xtensa -M esp32s3
```

Every S3 board (`esp32-s3`, `xiao-esp32-s3`, `arduino-nano-esp32`, ...) maps to that same
emulated machine. So **adding a board is a frontend-only job**: an id, a label, a pinout,
a visual, its options, and its compile target (FQBN). You never touch QEMU or the backend.

> Corollary: a new board is CPU-accurate for free, but adds **no** new peripheral
> emulation. External chips are separate canvas "components".

## REQUIRED edits (board appears + correct identity/options/visual)

These are the edits our `velxio-patch/patch_velxio.py` applies automatically. All under
`frontend/src/`. Chosen id: `waveshare-esp32-s3-touch-lcd-2.8`.

| File | Symbol | Add |
|---|---|---|
| `types/board.ts` | `BoardKind` union | `\| 'your-id' // comment` |
| `types/board.ts` | `BOARD_SUPPORTS_MICROPYTHON` set | `'your-id',` |
| `types/board.ts` | `BOARD_SUPPORTS_ESPIDF` set | `'your-id',` |
| `types/board.ts` | `BOARD_KIND_LABELS` | `'your-id': 'Nice Name',` |
| `types/board.ts` | `BOARD_KIND_FQBN` | `'your-id': 'esp32:esp32:esp32s3',` |
| `components/ComponentPickerModal.tsx` | `ALL_BOARDS` | `'your-id',` (this is what makes the tile show up) |
| `components/ComponentPickerModal.tsx` | `BOARD_DESCRIPTIONS` | `'your-id': 'one-liner',` |
| `components/ComponentPickerModal.tsx` | `BOARD_TAG` | `'your-id': 'ESP32-S3',` |
| `types/boardOptions.ts` | `ESP32_S3_KINDS` set | `'your-id',` (makes it behave/route as S3) |
| `types/boardOptions.ts` | `getDefaultOptionsForKind()` | an `if` setting `flashSize`/`psram` for your module |
| `components/velxio-components/Esp32Element.ts` | the visual config map | `'your-id': { svgUrl: esp32S3SvgUrl, w: 128, h: 350, pins: PINS_ESP32_S3 }` (reuse the S3 DevKit skin) |
| `utils/boardPinMapping.ts` | `BOARD_COMPONENT_IDS` | `'your-id',` |

The board tile thumbnail is rendered from the board's own element (from `Esp32Element.ts`),
so once the visual entry exists the picture appears automatically. No separate image asset.

## RECOMMENDED edits (needed for a clean production build)

Several maps are `Record<BoardKind, ...>`, which TypeScript requires to be **exhaustive**.
`vite` dev mode uses esbuild and does **not** typecheck, so Level 1 testing works without
these. But `tsc` / `vite build` (and the Docker image build) will **fail** until every one
has your id. Find them with:

```bash
grep -rnE 'Record<BoardKind' frontend/src
```

At minimum add your id (reusing an `esp32-s3` value is fine) to:
`ComponentPickerModal` also has none beyond the above; but check
`components/editor/EditorToolbar.tsx` (`BOARD_PILL_ICON`, `BOARD_PILL_COLOR`),
`components/editor/FileExplorer.tsx` (`BOARD_ICON`, `BOARD_COLOR`),
`components/simulator/BoardPickerModal.tsx` (`BOARD_DESCRIPTIONS`, `BOARD_ICON`).

For full runtime S3 behavior, also add your id to the scattered hard-coded checks
(`grep -rn "=== 'esp32-s3'" frontend/src`) in `Esp32Bridge.ts`, `useSimulatorStore.ts`,
`Interconnect.ts`, `SimulatorCanvas.tsx`, `Esp32MicroPythonLoader.ts`. (The codebase does
not route all of these through `ESP32_S3_KINDS`, so the set alone is not enough for them.)

## Automated patch

```bash
python3 velxio-patch/patch_velxio.py /path/to/velxio     # applies the REQUIRED edits
```
It self-reports each insertion and prints `MISS` if an anchor moved. Run once on a clean
checkout (`git checkout -- .` to reset).

## Build, run, and test

See [`testing-checklist.md`](testing-checklist.md) for the full checklist. Short version:

- **Level 1 (frontend only, no account):** `cd frontend && npm install && ./node_modules/.bin/vite --host`, open <http://localhost:5173>, confirm the board shows up with the right label/options/visual.
  - Gotcha: `npm run dev` runs a codegen step needing the **root** `typescript` dep; a
    frontend-only install lacks it. Run `vite` directly (generated files are committed).
- **Level 2 (compile + emulate):** needs Docker + a **free license key** from
  <https://velxio.dev/license/signup> (the OSS Docker build gates the QEMU `.so` binaries).
  Then `docker compose build --build-arg VELXIO_LICENSE_KEY=vlx_personal_... && docker compose up -d`, open <http://localhost:3080>.

## What you CANNOT get this way

Adding a board does not simulate the chips soldered to it. A display may work via a
generic TFT component; anything exotic (unusual touch controllers, IMUs, RTCs, codecs)
needs a **custom chip** (`docs/CUSTOM_CHIPS.md` + `frontend/src/components/customChips/
examples/*.chip.json`). Custom chips are digital/logic models and are a real project each;
some parts (e.g. a capacitive touch controller needing injected touch input) may not be
expressible at all.
