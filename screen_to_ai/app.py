from __future__ import annotations

import threading

from .compat import fix_six_metapath_importer
from dotenv import load_dotenv
from PySide6 import QtCore, QtWidgets

fix_six_metapath_importer()

from .config import AppConfig, load_config
from .deepseek import DeepSeekClient, DeepSeekConfig
from .hotkey import HotkeyListener
from .pipeline import CaptureResult, capture_and_ocr
from .ui import OverlayWindow


class Controller(QtCore.QObject):
    capture_done = QtCore.Signal(object)
    capture_failed = QtCore.Signal(str)
    hint_done = QtCore.Signal(str)
    hint_failed = QtCore.Signal(str)

    def __init__(self, cfg: AppConfig, overlay: OverlayWindow, deepseek: DeepSeekClient | None) -> None:
        super().__init__()
        self._cfg = cfg
        self._overlay = overlay
        self._deepseek = deepseek
        self._lock = threading.Lock()
        self._busy = False
        self._last_ocr = ""

    @QtCore.Slot()
    def trigger_capture(self) -> None:
        with self._lock:
            if self._busy:
                return
            self._busy = True
        self._overlay.reset_user_hidden()
        self._overlay.set_busy("截屏识别中…")

        def run() -> None:
            try:
                res = capture_and_ocr(self._cfg)
            except Exception as e:
                self.capture_failed.emit(str(e))
            else:
                self.capture_done.emit(res)

        threading.Thread(target=run, name="capture-ocr", daemon=True).start()

    @QtCore.Slot()
    def page_down(self) -> None:
        self._overlay.page_down()

    @QtCore.Slot()
    def page_up(self) -> None:
        self._overlay.page_up()

    @QtCore.Slot(object)
    def on_capture_done(self, res: CaptureResult) -> None:
        self._last_ocr = res.text
        if not self._deepseek or not self._last_ocr:
            self._overlay.set_hint("未配置 DEEPSEEK_API_KEY", status="提示")
            self._overlay.set_hint_enabled(False)
            with self._lock:
                self._busy = False
            return

        self._overlay.set_hint_enabled(True)
        self._overlay.set_text("DeepSeek", "", out_dir=self._cfg.out_dir, status="生成提示中…")

        def run() -> None:
            try:
                text = self._deepseek.generate_hints(self._last_ocr)
            except Exception as e:
                self.hint_failed.emit(str(e))
            else:
                self.hint_done.emit(text)

        threading.Thread(target=run, name="deepseek-hints", daemon=True).start()

    @QtCore.Slot(str)
    def on_capture_failed(self, msg: str) -> None:
        self._overlay.set_text("DeepSeek", msg, out_dir=self._cfg.out_dir, status="错误")
        self._overlay.set_hint_enabled(False)
        with self._lock:
            self._busy = False

    @QtCore.Slot()
    def trigger_hint(self) -> None:
        if not self._deepseek or not self._last_ocr:
            return
        with self._lock:
            if self._busy:
                return
            self._busy = True
        self._overlay.reset_user_hidden()
        self._overlay.set_busy("生成提示中…")

        def run() -> None:
            try:
                text = self._deepseek.generate_hints(self._last_ocr)
            except Exception as e:
                self.hint_failed.emit(str(e))
            else:
                self.hint_done.emit(text)

        threading.Thread(target=run, name="deepseek-hints", daemon=True).start()

    @QtCore.Slot(str)
    def on_hint_done(self, text: str) -> None:
        self._overlay.set_hint(text, status="完成")
        with self._lock:
            self._busy = False

    @QtCore.Slot(str)
    def on_hint_failed(self, msg: str) -> None:
        self._overlay.set_hint(msg, status="错误")
        with self._lock:
            self._busy = False


def run() -> None:
    load_dotenv(override=False)
    cfg = load_config()

    app = QtWidgets.QApplication([])
    lock = QtCore.QLockFile(
        str(
            (QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.TempLocation) or ".")
            + "/screenToAI.lock"
        )
    )
    lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        return
    overlay = OverlayWindow()

    deepseek = None
    if cfg.deepseek_api_key:
        deepseek = DeepSeekClient(
            DeepSeekConfig(api_key=cfg.deepseek_api_key, base_url=cfg.deepseek_base_url, model=cfg.deepseek_model)
        )

    controller = Controller(cfg, overlay, deepseek)
    controller.capture_done.connect(controller.on_capture_done)
    controller.capture_failed.connect(controller.on_capture_failed)
    controller.hint_done.connect(controller.on_hint_done)
    controller.hint_failed.connect(controller.on_hint_failed)
    overlay.request_hint.connect(controller.trigger_hint)

    hotkeys = {
        cfg.hotkey: lambda: QtCore.QMetaObject.invokeMethod(controller, "trigger_capture"),
        cfg.page_down_hotkey: lambda: QtCore.QMetaObject.invokeMethod(controller, "page_down"),
        cfg.page_up_hotkey: lambda: QtCore.QMetaObject.invokeMethod(controller, "page_up"),
    }
    hotkeys.setdefault("<ctrl>+<shift>+<down>", lambda: QtCore.QMetaObject.invokeMethod(controller, "page_down"))
    hotkeys.setdefault("<ctrl>+<shift>+<up>", lambda: QtCore.QMetaObject.invokeMethod(controller, "page_up"))

    listener = HotkeyListener(hotkeys)
    listener.start()

    def on_exit() -> None:
        listener.stop()

    app.aboutToQuit.connect(on_exit)
    app.exec()
