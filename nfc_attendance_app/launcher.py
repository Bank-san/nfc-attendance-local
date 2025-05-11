# nfc_attendance_app/launcher.py

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QApplication
from attendance.window import AttendanceWindow
from registration.window import RegisterWindow
from history.window import AttendanceHistoryWindow
from summary.window import AttendanceSummaryWindow
from manual.window import ManualEntryWindow
from registration.list_window import UserListWindow  # ← 追加

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFC出席管理システム")
        self.resize(300, 400)

        layout = QVBoxLayout()

        self.attendance_button = QPushButton("出席モード")
        self.attendance_button.clicked.connect(self.open_attendance)

        self.register_button = QPushButton("登録モード")
        self.register_button.clicked.connect(self.open_register)

        self.history_button = QPushButton("出席履歴")
        self.history_button.clicked.connect(self.open_history)

        self.summary_button = QPushButton("来場者分析")
        self.summary_button.clicked.connect(self.open_summary)

        self.manual_button = QPushButton("手動登録")
        self.manual_button.clicked.connect(self.open_manual)

        self.userlist_button = QPushButton("登録者リスト")  # ← 追加
        self.userlist_button.clicked.connect(self.open_user_list)

        for btn in [
            self.attendance_button, self.register_button, self.history_button,
            self.summary_button, self.manual_button, self.userlist_button
        ]:
            layout.addWidget(btn)

        self.setLayout(layout)

    def open_attendance(self):
        self.attendance_window = AttendanceWindow()
        self.attendance_window.show()

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

    def open_history(self):
        self.history_window = AttendanceHistoryWindow()
        self.history_window.show()

    def open_summary(self):
        self.summary_window = AttendanceSummaryWindow()
        self.summary_window.show()

    def open_manual(self):
        self.manual_window = ManualEntryWindow()
        self.manual_window.show()

    def open_user_list(self):  # ← 追加
        self.user_list_window = UserListWindow()
        self.user_list_window.show()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())
