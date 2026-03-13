from __future__ import annotations

import threading
from collections.abc import Callable

from .compat import fix_six_metapath_importer


class HotkeyListener:
    def __init__(self, hotkeys: dict[str, Callable[[], None]]):
        self._hotkeys = hotkeys
        self._listener: keyboard.GlobalHotKeys | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread:
            return

        fix_six_metapath_importer()

        try:
            from pynput import keyboard
        except Exception as e:
            raise RuntimeError(f"无法启动全局热键监听（pynput 导入失败）：{e}") from e

        def run() -> None:
            with keyboard.GlobalHotKeys(self._hotkeys) as h:
                self._listener = h
                h.join()

        self._thread = threading.Thread(target=run, name="hotkey-listener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
        self._listener = None
        self._thread = None
