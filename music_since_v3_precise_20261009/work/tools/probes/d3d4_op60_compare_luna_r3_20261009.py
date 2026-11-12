from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    ROOT / "research_assets/d3d4_op60_compare_luna_r3_20261009/cfeo_op60_60-1-BR_BritishLibrary/op60_p2_b14-23.jpg",
    ROOT / "research_assets/d3d4_20261009_luna_r2/cfeo_op60_60-1-BR_BritishLibrary/op60_p3_b24-33.jpg",
)


def jpeg_size(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("not a JPEG stream")
    i = 2
    while i < len(data):
        while i < len(data) and data[i] != 0xFF:
            i += 1
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > len(data):
            break
        length = struct.unpack(">H", data[i:i + 2])[0]
        if length < 2 or i + length > len(data):
            raise ValueError("invalid JPEG segment")
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height, width = struct.unpack(">HH", data[i + 3:i + 7])
            return width, height
        i += length
    raise ValueError("JPEG dimensions not found")


results = []
for path in FILES:
    raw = path.read_bytes()
    width, height = jpeg_size(raw)
    results.append({
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest().upper(),
        "width": width,
        "height": height,
        "jpeg_soi": raw[:2] == b"\xff\xd8",
    })
print(json.dumps(results, ensure_ascii=False, separators=(",", ":")))