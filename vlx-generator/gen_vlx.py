#!/usr/bin/env python3
"""
Generate an importable Velxio `.vlx` project from a small `board-spec.json`.

Purpose: model a CUSTOM board (its MCU + interfaces + pinout) so firmware written
for that board can be compiled and run in the Velxio simulator BEFORE the hardware
exists. Import the output via Velxio -> File -> Open project.

Usage:
    python3 gen_vlx.py board-spec.json [out.vlx]

Spec format (board-spec.json):
{
  "name": "My Custom Board",
  "boardKind": "esp32-s3",              # any Velxio boardKind (esp32-s3, esp32, esp32-c3, ...)
  "firmware": "sketch.ino",             # path relative to the spec, OR inline "code": "..."
  "libraries": ["Adafruit ILI9341"],    # optional Arduino libraries to declare
  "interfaces": [                       # the peripherals on the board
    { "id": "tft1", "part": "ili9341", "properties": {} }
  ],
  "pinout": [                           # THE PINOUT: board GPIO -> interface pin
    { "gpio": "45", "to": "tft1:MOSI", "color": "#ff8800" },
    { "gpio": "GND.1", "to": "tft1:GND" }
  ]
}

Rules baked in (learned from Velxio's source + a working import):
  - The file-group key MUST be `group-<boardId>`; the board id is set to boardKind,
    and wires reference the board by that id.
  - Component `metadataId` is the Velxio/Wokwi part name with the `wokwi-`/`velxio-`
    prefix stripped (e.g. `wokwi-ili9341` -> `ili9341`).
  - Board pins are referenced by GPIO number as a string (`"45"`) plus named power
    pins (`"3V3.1"`, `"3V3.2"`, `"5V"`, `"GND.1"`..`"GND.4"`).
  - The interface `part` must be an existing Velxio component; anything Velxio does
    not model needs a custom chip (see the repo README).
"""
import json
import sys
import datetime
import pathlib

PALETTE = ["#ff8800", "#00aaff", "#00cc00", "#cc0000",
           "#ffffff", "#ffaa44", "#8800ff", "#ffff00"]


def strip_prefix(part):
    for p in ("wokwi-", "velxio-"):
        if part.startswith(p):
            return part[len(p):]
    return part


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 gen_vlx.py board-spec.json [out.vlx]")

    spec_path = pathlib.Path(sys.argv[1])
    spec = json.loads(spec_path.read_text())

    board_kind = spec["boardKind"]
    board_id = board_kind               # wires reference the board by this id
    group_id = f"group-{board_id}"      # MUST match `group-<boardId>`

    # firmware: inline "code" or a file path relative to the spec
    if "code" in spec:
        code = spec["code"]
    else:
        fw = spec.get("firmware", "sketch.ino")
        code = (spec_path.parent / fw).read_text()

    components = []
    for i, itf in enumerate(spec.get("interfaces", [])):
        components.append({
            "id": itf["id"],
            "metadataId": strip_prefix(itf["part"]),
            "x": itf.get("x", 470),
            "y": itf.get("y", 70 + i * 160),
            "properties": itf.get("properties", {}),
        })

    wires = []
    for i, w in enumerate(spec.get("pinout", [])):
        comp_id, _, pin = w["to"].partition(":")
        if not pin:
            sys.exit(f"pinout entry {i}: 'to' must be 'componentId:pinName', got {w['to']!r}")
        wires.append({
            "id": f"w{i}",
            "start": {"componentId": board_id, "pinName": str(w["gpio"]), "x": 0, "y": 0},
            "end":   {"componentId": comp_id,   "pinName": pin,           "x": 0, "y": 0},
            "waypoints": [],
            "color": w.get("color", PALETTE[i % len(PALETTE)]),
        })

    board = {
        "id": board_id,
        "name": spec.get("name", board_kind),
        "boardKind": board_kind,
        "x": spec.get("x", 60),
        "y": spec.get("y", 80),
        "activeFileGroupId": group_id,
        "languageMode": spec.get("languageMode", "arduino"),
        "serialBaudRate": spec.get("serialBaudRate", 115200),
    }
    if spec.get("libraries"):
        board["libraries"] = spec["libraries"]

    payload = {
        "format": "velxio-project",
        "version": 1,
        "exportedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "name": spec.get("name", board_kind),
        "boards": [board],
        "fileGroups": {group_id: [{"name": "sketch.ino", "content": code}]},
        "components": components,
        "wires": wires,
        "activeBoardId": board_id,
    }

    if len(sys.argv) > 2:
        out = pathlib.Path(sys.argv[2])
    else:
        slug = spec.get("name", board_kind).lower().replace(" ", "-")
        out = spec_path.parent / f"{slug}.vlx"
    out.write_text(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    print(f"  boardKind={board_kind}  interfaces={len(components)}  wires={len(wires)}")


if __name__ == "__main__":
    main()
