from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import APP_STYLESHEET, build_light_palette


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SENTRA")
    app.setOrganizationName("SENTRA")
    app.setStyle("Fusion")
    app.setPalette(build_light_palette())
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
