from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets


class OverlayWindow(QtWidgets.QWidget):
    request_hint = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("screenToAI")
        self.setWindowFlags(
            QtCore.Qt.WindowType.Tool
            | QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._frame = QtWidgets.QFrame(self)
        self._frame.setObjectName("frame")
        self._frame.setStyleSheet(
            "#frame{background-color:rgba(20,20,20,160);border:1px solid rgba(255,255,255,40);border-radius:10px;}"
        )

        self._title = QtWidgets.QLabel("OCR")
        self._title.setStyleSheet("color:#ddd;font-weight:600;")

        self._status = QtWidgets.QLabel("")
        self._status.setStyleSheet("color:#aaa;")

        self._text = QtWidgets.QTextBrowser()
        self._text.setOpenExternalLinks(True)
        self._text.setStyleSheet(
            "QTextBrowser{background:transparent;color:#eee;border:1px solid rgba(255,255,255,40);border-radius:6px;}"
        )

        self._btn_copy = QtWidgets.QPushButton("复制")
        self._btn_hide = QtWidgets.QPushButton("隐藏")
        self._btn_open = QtWidgets.QPushButton("打开目录")
        self._btn_hint = QtWidgets.QPushButton("生成提示")
        self._btn_hint.setEnabled(False)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self._btn_copy)
        btn_row.addWidget(self._btn_open)
        btn_row.addStretch(1)
        btn_row.addWidget(self._btn_hint)
        btn_row.addWidget(self._btn_hide)

        top_row = QtWidgets.QHBoxLayout()
        top_row.addWidget(self._title)
        top_row.addStretch(1)
        top_row.addWidget(self._status)

        layout = QtWidgets.QVBoxLayout(self._frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        layout.addLayout(top_row)
        layout.addWidget(self._text, 1)
        layout.addLayout(btn_row)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)

        self._last_dir: Path | None = None
        self._user_hidden = False
        self._copy_source = ""

        self._btn_hide.clicked.connect(self._on_hide_clicked)
        self._btn_copy.clicked.connect(self._copy)
        self._btn_open.clicked.connect(self._open_dir)
        self._btn_hint.clicked.connect(self.request_hint.emit)

        self.resize(520, 360)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super().showEvent(event)
        self._move_bottom_right()

    def set_text(self, title: str, text: str, out_dir: Path | None = None, status: str = "") -> None:
        self._title.setText(title)
        self._text.setPlainText(text)
        self._status.setText(status)
        self._copy_source = text
        if out_dir is not None:
            self._last_dir = out_dir
        if not self._user_hidden:
            if not self.isVisible():
                self.show()
            self.raise_()
            self.activateWindow()

    def set_markdown(self, title: str, markdown: str, out_dir: Path | None = None, status: str = "") -> None:
        self._title.setText(title)
        self._text.setMarkdown(markdown)
        self._status.setText(status)
        self._copy_source = markdown
        if out_dir is not None:
            self._last_dir = out_dir
        if not self._user_hidden:
            if not self.isVisible():
                self.show()
            self.raise_()
            self.activateWindow()

    def set_ocr(self, text: str, out_dir: Path, status: str = "") -> None:
        self.set_text("OCR", text, out_dir=out_dir, status=status)

    def set_hint_enabled(self, enabled: bool) -> None:
        self._btn_hint.setEnabled(enabled)

    def set_hint(self, text: str, status: str = "") -> None:
        self.set_markdown("DeepSeek", text, status=status)

    def set_busy(self, status: str) -> None:
        self._status.setText(status)
        if not self._user_hidden:
            if not self.isVisible():
                self.show()
            self.raise_()
            self.activateWindow()

    def reset_user_hidden(self) -> None:
        self._user_hidden = False

    def _on_hide_clicked(self) -> None:
        self._user_hidden = True
        self.hide()

    def _copy(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self._copy_source or self._text.toPlainText())

    def _open_dir(self) -> None:
        if not self._last_dir:
            return
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(self._last_dir)))

    @QtCore.Slot()
    def page_down(self) -> None:
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.value() + sb.pageStep())

    @QtCore.Slot()
    def page_up(self) -> None:
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.value() - sb.pageStep())

    def _move_bottom_right(self) -> None:
        screen = QtGui.QGuiApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        margin = 16
        x = geo.x() + geo.width() - self.width() - margin
        y = geo.y() + geo.height() - self.height() - margin
        self.move(x, y)
