from PyQt6.QtWidgets import QApplication
from launcher import LauncherWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())
