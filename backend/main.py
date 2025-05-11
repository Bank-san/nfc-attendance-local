# main.py
import sys
from PyQt6.QtWidgets import QApplication
from launcher import LauncherWindow  # ランチャー画面をインポート

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = LauncherWindow()  # ← ランチャーウィンドウを起動
    launcher.show()
    sys.exit(app.exec())
