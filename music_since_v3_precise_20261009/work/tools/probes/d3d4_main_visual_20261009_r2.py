"""Create fresh local score inspection views; never execute downloaded content."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


VIEWS = (
    ("p2_system2_mm16_17.png", "p2", (650, 1375, 3650, 2150), "p.2 system 2; conditional mm.16-17"),
    ("p2_system3_mm18_19.png", "p2", (650, 2125, 3650, 2925), "p.2 system 3; conditional mm.18-19"),
    ("p2_system4_mm20_21.png", "p2", (650, 2875, 3650, 3675), "p.2 system 4; conditional mm.20-21"),
    ("p2_system5_mm22_23.png", "p2", (650, 3575, 3650, 4350), "p.2 system 5; conditional mm.22-23"),
    ("p3_system1_mm24_25.png", "p3", (250, 675, 3225, 1425), "p.3 system 1; conditional mm.24-25"),
    ("p3_system2_mm26_27.png", "p3", (250, 1425, 3225, 2200), "p.3 system 2; conditional mm.26-27"),
    ("p3_system3_mm28_29.png", "p3", (250, 2125, 3225, 2875), "p.3 system 3; conditional mm.28-29"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p2", type=Path, required=True)
    parser.add_argument("--p3", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    for source in (args.p2, args.p3):
        if not source.is_file():
            raise ValueError("source image not found")
    args.out_dir.mkdir(parents=True, exist_ok=False)
    rows = []
    for name, key, box, locator in VIEWS:
        source = getattr(args, key)
        with Image.open(source) as image:
            if image.size != (3895, 5000):
                raise ValueError("unexpected source dimensions")
            cropped = image.crop(box)
            output = args.out_dir / name
            with output.open("xb") as stream:
                cropped.save(stream, format="PNG")
            raw = output.read_bytes()
            rows.append({"file": name, "parent": source.name, "box_original_px": box,
                         "dimensions_px": cropped.size, "locator": locator,
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    report = {"schema": "main-score-inspection-views/1", "date": "2026-10-09",
              "views": rows, "independent_sources": False,
              "parent_hash_remeasurement": False,
              "limits": ["Locators inherit researcher CFEO start bars and main visual barline counts.",
                         "Crop filenames are not evidence of successful visual interpretation.",
                         "No remote identity, theme identification or audio verification."],
              "network_calls": 0, "model_submissions": 0}
    with (args.out_dir / "crop_manifest.json").open("x", encoding="utf-8", newline="") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps({"new_views": len(rows), "output": str(args.out_dir),
                      "network_calls": 0, "model_submissions": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
