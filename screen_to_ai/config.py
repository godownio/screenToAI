from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    hotkey: str
    page_down_hotkey: str
    page_up_hotkey: str
    out_dir: Path
    ocr_provider: str
    ocr_lang: str
    tesseract_cmd: str | None
    aliyun_access_key_id: str | None
    aliyun_access_key_secret: str | None
    aliyun_ocr_endpoint: str
    tencent_secret_id: str | None
    tencent_secret_key: str | None
    tencent_region: str
    tencent_ocr_mode: str
    deepseek_api_key: str | None
    deepseek_base_url: str
    deepseek_model: str


def load_config() -> AppConfig:
    out_dir = Path(os.environ.get("SCREEN_TO_AI_OUT_DIR", ".screen_to_ai")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    tesseract_cmd = os.environ.get("TESSERACT_CMD")
    if not tesseract_cmd:
        guess = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        if guess.exists():
            tesseract_cmd = str(guess)

    ocr_provider = os.environ.get("SCREEN_TO_AI_OCR_PROVIDER", "").strip().lower()
    if not ocr_provider:
        if os.environ.get("TENCENT_SECRET_ID") and os.environ.get("TENCENT_SECRET_KEY"):
            ocr_provider = "tencent"
        elif os.environ.get("ALIYUN_ACCESS_KEY_ID") and os.environ.get("ALIYUN_ACCESS_KEY_SECRET"):
            ocr_provider = "aliyun"
        else:
            ocr_provider = "tesseract"

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    return AppConfig(
        hotkey=os.environ.get("SCREEN_TO_AI_HOTKEY", "<ctrl>+<shift>+o"),
        page_down_hotkey=os.environ.get("SCREEN_TO_AI_PAGE_DOWN_HOTKEY", "<ctrl>+<shift>+l"),
        page_up_hotkey=os.environ.get("SCREEN_TO_AI_PAGE_UP_HOTKEY", "<ctrl>+<shift>+p"),
        out_dir=out_dir,
        ocr_provider=ocr_provider,
        ocr_lang=os.environ.get("SCREEN_TO_AI_OCR_LANG", "eng"),
        tesseract_cmd=tesseract_cmd,
        aliyun_access_key_id=os.environ.get("ALIYUN_ACCESS_KEY_ID"),
        aliyun_access_key_secret=os.environ.get("ALIYUN_ACCESS_KEY_SECRET"),
        aliyun_ocr_endpoint=os.environ.get("ALIYUN_OCR_ENDPOINT", "ocr-api.cn-hangzhou.aliyuncs.com"),
        tencent_secret_id=os.environ.get("TENCENT_SECRET_ID"),
        tencent_secret_key=os.environ.get("TENCENT_SECRET_KEY"),
        tencent_region=os.environ.get("TENCENT_REGION", "ap-guangzhou"),
        tencent_ocr_mode=os.environ.get("TENCENT_OCR_MODE", "accurate"),
        deepseek_api_key=os.environ.get("DEEPSEEK_API_KEY"),
        deepseek_base_url=base_url,
        deepseek_model=model,
    )
