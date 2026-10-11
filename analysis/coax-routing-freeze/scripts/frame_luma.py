#!/usr/bin/env python3
"""Objective frame-brightness statistics for a RAW 8-bit grayscale frame on stdin.

Purpose
-------
The coax-routing-freeze card needs physical observation (route a bundle, read a
caliper, read a jacket legend). On this host the only possible visual channel is
a v4l2 camera, so before declaring "no physical access" we measure what that
camera actually returns. A covered lens / closed shutter produces a frame with a
near-zero mean and a collapsed palette -- that is a *measurement*, not an
opinion, and it is what makes the gap evidence instead of an excuse.

Reads headerless raw gray bytes from stdin so it needs no image library.

Usage
-----
    ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 -f rawvideo -pix_fmt gray - \
        | python3 frame_luma.py 640 480
"""
from __future__ import annotations

import json
import sys


def main(argv: list[str]) -> int:
    width = int(argv[0]) if argv else 640
    height = int(argv[1]) if len(argv) > 1 else 480
    data = sys.stdin.buffer.read()
    if not data:
        print(json.dumps({"ok": False, "reason": "no frame bytes on stdin"}))
        return 3

    n = len(data)
    total = sum(data)
    yavg = total / n
    ymax = max(data)
    ymin = min(data)
    palette = len(set(data))

    # A usable frame of a real scene is neither pitch black nor a flat field.
    # Thresholds are deliberately generous: YAVG/255 < 0.05 or a palette of a
    # handful of levels means the sensor is not seeing a scene at all.
    usable = yavg >= 12.75 and palette >= 32  # 12.75/255 == 0.05

    print(json.dumps({
        "ok": True,
        "declared_size": [width, height],
        "bytes_read": n,
        "bytes_expected": width * height,
        "yavg_255": round(yavg, 2),
        "yavg_norm": round(yavg / 255.0, 4),
        "ymin": ymin,
        "ymax": ymax,
        "distinct_levels": palette,
        "usable_scene": usable,
        "verdict": ("frame carries a scene" if usable
                    else "frame is effectively black/flat -- sensor sees no scene"),
    }, indent=1))
    return 0 if usable else 4


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
