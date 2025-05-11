import sys
from PyQt6.QtWidgets import QApplication
from launcher import LauncherWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = LauncherWindow()
    launcher.show()
    sys.exit(app.exec())