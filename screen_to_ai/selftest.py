from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

from .config import load_config
from .deepseek import DeepSeekClient, DeepSeekConfig
from .ocr import ocr_image
from .screenshot import capture_primary_screen_png


def _mask(s: str | None) -> str:
    if not s:
        return "<empty>"
    if len(s) <= 8:
        return "<set>"
    return f"{s[:3]}...{s[-3:]}"

def _redact(text: str) -> str:
    patterns = [
        r"sk-[A-Za-z0-9]{10,}",
        r"AKID[A-Za-z0-9]{10,}",
        r"AKI[A-Za-z0-9]{10,}",
        r"(?i)secret[_-]?key\\s*[:=]\\s*[^\\s\"']+",
        r"(?i)access[_-]?key\\s*[:=]\\s*[^\\s\"']+",
    ]
    for p in patterns:
        text = re.sub(p, "<redacted>", text)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="screen_to_ai.selftest")
    parser.add_argument("--image", type=str, default="", help="使用已有图片路径做 OCR（不传则自动截屏）")
    parser.add_argument("--no-deepseek", action="store_true", help="仅测试 OCR，不调用 DeepSeek")
    parser.add_argument("--save", action="store_true", help="保存中间结果到输出目录")
    args = parser.parse_args(argv)

    load_dotenv(override=False)
    cfg = load_config()

    print("Config:")
    print(f"  OCR provider: {cfg.ocr_provider}")
    if cfg.ocr_provider == "tencent":
        print(f"  TENCENT_SECRET_ID: {_mask(os.environ.get('TENCENT_SECRET_ID'))}")
        print(f"  TENCENT_REGION: {cfg.tencent_region}")
        print(f"  TENCENT_OCR_MODE: {cfg.tencent_ocr_mode}")
    if cfg.ocr_provider == "tesseract":
        print(f"  OCR lang: {cfg.ocr_lang}")
        print(f"  TESSERACT_CMD: {cfg.tesseract_cmd or '<auto>'}")
    print(f"  OUT_DIR: {cfg.out_dir}")
    print(f"  DEEPSEEK_API_KEY: {_mask(cfg.deepseek_api_key)}")

    if args.image:
        img_path = Path(args.image).expanduser().resolve()
        if not img_path.exists():
            print(f"Image not found: {img_path}", file=sys.stderr)
            return 2
    else:
        img_path = capture_primary_screen_png(cfg.out_dir if args.save else Path.cwd())

    print(f"Image: {img_path}")
    try:
        text = ocr_image(img_path, cfg)
    except Exception as e:
        print(f"OCR failed: {e}", file=sys.stderr)
        return 3

    print(f"OCR ok: {len(text)} chars")
    preview = _redact(text[:400]).replace("\n", "\\n")
    print(f"OCR preview: {preview}")

    if args.save:
        cfg.out_dir.mkdir(parents=True, exist_ok=True)
        (cfg.out_dir / "selftest_ocr.txt").write_text(_redact(text), encoding="utf-8")

    if args.no_deepseek:
        return 0

    if not cfg.deepseek_api_key:
        print("DeepSeek skipped: DEEPSEEK_API_KEY not set", file=sys.stderr)
        return 4

    print("DeepSeek: calling...")
    client = DeepSeekClient(
        DeepSeekConfig(api_key=cfg.deepseek_api_key, base_url=cfg.deepseek_base_url, model=cfg.deepseek_model)
    )
    try:
        ans = client.generate_hints(text)
    except Exception as e:
        print(f"DeepSeek failed: {e}", file=sys.stderr)
        return 5

    print(f"DeepSeek ok: {len(ans)} chars")
    print("DeepSeek answer:")
    safe_ans = _redact(ans)
    print(safe_ans)
    if args.save:
        (cfg.out_dir / "selftest_deepseek.txt").write_text(safe_ans, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
