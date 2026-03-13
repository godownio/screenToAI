from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig
from .ocr import ocr_image
from .screenshot import capture_primary_screen_png


@dataclass(frozen=True)
class CaptureResult:
    image_path: Path
    text_path: Path
    text: str


def capture_and_ocr(cfg: AppConfig) -> CaptureResult:
    img_path = capture_primary_screen_png(cfg.out_dir)
    text = ocr_image(img_path, cfg)
    txt_path = img_path.with_suffix(".txt")
    txt_path.write_text(text, encoding="utf-8")
    return CaptureResult(image_path=img_path, text_path=txt_path, text=text)
