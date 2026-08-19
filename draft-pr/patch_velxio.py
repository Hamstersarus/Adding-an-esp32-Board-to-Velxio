#!/usr/bin/env python3
"""
Add the Waveshare ESP32-S3-Touch-LCD-2.8 board to a local Velxio checkout.

Usage:
    python3 patch_velxio.py /path/to/velxio

Verified against davidmonterocrespo24/velxio (fetched 2026-08). It inserts our
board id after each map/set declaration, so it is order-independent and each
insertion is self-reported. Re-running will duplicate entries, so run once on a
clean checkout (git checkout -- . to reset).

This covers the REQUIRED edits (board appears + correct identity/options/visual).
For a production-clean build also do the RECOMMENDED edits listed in CHANGES.md
(cosmetic Record<BoardKind> maps + the scattered `kind === 'esp32-s3' || ...`
behavior checks), otherwise `tsc`/`vite build` will fail on exhaustive maps
(the `vite` dev server does not typecheck, so Level 1 testing still works).
"""
import sys
import pathlib

if len(sys.argv) < 2:
    sys.exit("usage: python3 patch_velxio.py /path/to/velxio")

SRC = pathlib.Path(sys.argv[1]) / 'frontend' / 'src'
ID = 'waveshare-esp32-s3-touch-lcd-2.8'

EDITS = [
    ('types/board.ts', 'export type BoardKind =',
     f"  | '{ID}' // Waveshare ESP32-S3 Touch LCD 2.8 (N16R8), QEMU (esp32-s3)"),
    ('types/board.ts', 'export const BOARD_SUPPORTS_MICROPYTHON = new Set<BoardKind>([',
     f"  '{ID}',"),
    ('types/board.ts', 'export const BOARD_SUPPORTS_ESPIDF = new Set<BoardKind>([',
     f"  '{ID}',"),
    ('types/board.ts', 'export const BOARD_KIND_LABELS: Record<BoardKind, string> = {',
     f"  '{ID}': 'Waveshare ESP32-S3 Touch LCD 2.8',"),
    ('types/board.ts', 'export const BOARD_KIND_FQBN: Record<BoardKind, string | null> = {',
     f"  '{ID}': 'esp32:esp32:esp32s3',"),
    ('components/ComponentPickerModal.tsx', 'const ALL_BOARDS: BoardKind[] = [',
     f"  '{ID}',"),
    ('components/ComponentPickerModal.tsx', 'const BOARD_DESCRIPTIONS: Record<BoardKind, string> = {',
     f"  '{ID}': 'Waveshare 2.8\" touch LCD: ESP32-S3 N16R8, ST7789 + CST3530',"),
    ('components/ComponentPickerModal.tsx', 'const BOARD_TAG: Partial<Record<BoardKind, string>> = {',
     f"  '{ID}': 'ESP32-S3',"),
    ('types/boardOptions.ts', 'const ESP32_S3_KINDS: ReadonlySet<BoardKind> = new Set([',
     f"  '{ID}',"),
    ('types/boardOptions.ts', 'const defaults = { ...DEFAULT_ESP32_OPTIONS };',
     f"  if (kind === '{ID}') {{ defaults.flashSize = '16MB'; defaults.psram = 'opi'; }}"),
    ('components/velxio-components/Esp32Element.ts', "'esp32-s3': { svgUrl: esp32S3SvgUrl",
     f"  '{ID}': {{ svgUrl: esp32S3SvgUrl, w: 128, h: 350, pins: PINS_ESP32_S3 }},"),
    ('utils/boardPinMapping.ts', 'const BOARD_COMPONENT_IDS',
     f"  '{ID}',"),
]

for rel, anchor, insert in EDITS:
    f = SRC / rel
    lines = f.read_text().split('\n')
    for i, ln in enumerate(lines):
        if anchor in ln:
            lines.insert(i + 1, insert)
            f.write_text('\n'.join(lines))
            print(f"OK   {rel}: after '{anchor[:42]}...'")
            break
    else:
        print(f"MISS {rel}: ANCHOR NOT FOUND -> '{anchor[:50]}'")
