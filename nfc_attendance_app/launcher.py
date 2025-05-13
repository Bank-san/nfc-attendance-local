from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QSizePolicy
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt
from attendance.window import AttendanceWindow
from registration.window import RegisterWindow
from history.window import AttendanceHistoryWindow
from summary.window import AttendanceSummaryWindow
from manual.window import ManualEntryWindow
from registration.list_window import UserListWindow

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("出席管理システム - メニュー")
        self.resize(800, 600)

        # 背景グラデーションカラー
        palette = QPalette()
        gradient = QColor(255, 140, 0)
        palette.setColor(QPalette.ColorRole.Window, gradient)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("出席管理システム")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        button_grid = QGridLayout()
        button_grid.setSpacing(20)

        self.attendance_window = AttendanceWindow()

        buttons = [
            ("出席モード", self.open_attendance),
            ("登録モード", self.open_register),
            ("出席履歴", self.open_history),
            ("来場分析", self.open_summary),
            ("手動登録", self.open_manual),
            ("登録者リスト", self.open_user_list),
        ]

        for i, (label, callback) in enumerate(buttons):
            btn = QPushButton(label)
            btn.setFont(QFont("Arial", 14))
            btn.setFixedSize(180, 80)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #ff8c00;
                    border-radius: 10px;
                    color: #ff8c00;
                }
                QPushButton:hover {
                    background-color: #ffe0b2;
                }
            """)
            row, col = divmod(i, 3)
            button_grid.addWidget(btn, row, col)

        layout.addLayout(button_grid)
        self.setLayout(layout)

    def open_attendance(self):
        self.attendance_window.show()
        self.attendance_window.resume_attendance_mode()

    def open_register(self):
        self.attendance_window.worker.mode = "registration"
        self.register_window = RegisterWindow(attendance_window=self.attendance_window)
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

    def open_user_list(self):
        self.user_list_window = UserListWindow()
        self.user_list_window.show()
