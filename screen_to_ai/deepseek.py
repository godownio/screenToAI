from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    base_url: str
    model: str


class DeepSeekClient:
    def __init__(self, cfg: DeepSeekConfig, timeout_s: int = 60) -> None:
        self._cfg = cfg
        self._timeout_s = timeout_s

    def generate_hints(self, problem_text: str) -> str:
        url = f"{self._cfg.base_url}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self._cfg.api_key}", "Content-Type": "application/json"}
        messages = [
            {
                "role": "system",
                "content": "你是算法教练。只给关键思路、代码（无需注释）。",
            },
            {
                "role": "user",
                "content": _prompt(problem_text),
            },
        ]
        payload = {"model": self._cfg.model, "messages": messages, "temperature": 0.2}
        resp = requests.post(url, headers=headers, json=payload, timeout=self._timeout_s)
        resp.raise_for_status()
        data = resp.json()
        return _extract_content(data).strip()


def _extract_content(data: dict) -> str:
    choices = data.get("choices")
    if not choices:
        raise ValueError("DeepSeek 响应缺少 choices")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not isinstance(content, str):
        raise ValueError("DeepSeek 响应缺少 message.content")
    return content


def _prompt(problem_text: str) -> str:
    return (
        "请根据以下题面给出解题提示，结构化输出：\n"
        "1) 推荐算法与步骤（只需一个算法）\n"
        "2) 可运行代码\n"
        f"题面：\n{problem_text}"
    )
