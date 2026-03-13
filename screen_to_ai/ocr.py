from __future__ import annotations

import base64
import json
from pathlib import Path

from PIL import Image

from .config import AppConfig


def ocr_image(image_path: Path, cfg: AppConfig) -> str:
    if cfg.ocr_provider == "tencent":
        return _normalize_text(_ocr_tencent(image_path, cfg))
    if cfg.ocr_provider == "aliyun":
        return _normalize_text(_ocr_aliyun(image_path, cfg))
    return _normalize_text(_ocr_tesseract(image_path, tesseract_cmd=cfg.tesseract_cmd, lang=cfg.ocr_lang))


def _ocr_tesseract(image_path: Path, tesseract_cmd: str | None, lang: str) -> str:
    import pytesseract

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    with Image.open(image_path) as im:
        return pytesseract.image_to_string(im, lang=lang)


def _ocr_tencent(image_path: Path, cfg: AppConfig) -> str:
    if not cfg.tencent_secret_id or not cfg.tencent_secret_key:
        raise RuntimeError("未配置腾讯云 OCR：请设置 TENCENT_SECRET_ID / TENCENT_SECRET_KEY")

    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.ocr.v20181119 import ocr_client, models
    except Exception as e:
        raise RuntimeError("缺少腾讯云 OCR SDK：pip install tencentcloud-sdk-python") from e

    cred = credential.Credential(cfg.tencent_secret_id, cfg.tencent_secret_key)
    http_profile = HttpProfile()
    http_profile.endpoint = "ocr.tencentcloudapi.com"
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client = ocr_client.OcrClient(cred, cfg.tencent_region, client_profile)

    mode = (cfg.tencent_ocr_mode or "").strip().lower()
    if mode in ("basic", "generalbasicocr"):
        req = models.GeneralBasicOCRRequest()
        api = client.GeneralBasicOCR
    else:
        req = models.GeneralAccurateOCRRequest()
        api = client.GeneralAccurateOCR

    req.ImageBase64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    resp = api(req)
    detections = getattr(resp, "TextDetections", None) or []
    lines: list[str] = []
    for d in detections:
        txt = getattr(d, "DetectedText", None)
        if isinstance(txt, str) and txt:
            lines.append(txt)
    return "\n".join(lines)



def _ocr_aliyun(image_path: Path, cfg: AppConfig) -> str:
    if not cfg.aliyun_access_key_id or not cfg.aliyun_access_key_secret:
        raise RuntimeError("未配置阿里云 OCR：请设置 ALIYUN_ACCESS_KEY_ID / ALIYUN_ACCESS_KEY_SECRET")
    try:
        from alibabacloud_ocr_api20210707.client import Client as OcrClient
        from alibabacloud_ocr_api20210707 import models as ocr_models
        from alibabacloud_tea_openapi.models import Config as OpenApiConfig
    except Exception as e:
        raise RuntimeError("缺少阿里云 OCR SDK：pip install alibabacloud_ocr_api20210707") from e

    openapi_cfg = OpenApiConfig(access_key_id=cfg.aliyun_access_key_id, access_key_secret=cfg.aliyun_access_key_secret)
    openapi_cfg.endpoint = cfg.aliyun_ocr_endpoint
    client = OcrClient(openapi_cfg)

    body = image_path.read_bytes()
    req = ocr_models.RecognizeGeneralRequest(body=body)
    resp = client.recognize_general(req)

    data = getattr(getattr(resp, "body", resp), "data", None)
    if not isinstance(data, str) or not data:
        raise RuntimeError("阿里云 OCR 响应异常：缺少 Data")

    payload = _extract_json_object(data)
    content = payload.get("content")
    if not isinstance(content, str):
        raise RuntimeError("阿里云 OCR 响应异常：缺少 content")
    return content


def _extract_json_object(data: str) -> dict:
    start = data.find("{")
    if start == -1:
        raise RuntimeError("阿里云 OCR 响应异常：Data 不是 JSON")
    return json.loads(data[start:])


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()
