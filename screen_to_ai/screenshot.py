from __future__ import annotations

from datetime import datetime
from pathlib import Path

import mss
import mss.tools


def capture_primary_screen_png(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    out_path = out_dir / f"shot_{ts}.png"
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        mss.tools.to_png(img.rgb, img.size, output=str(out_path))
    return out_path
