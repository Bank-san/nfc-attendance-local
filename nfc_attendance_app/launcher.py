from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from attendance.window import AttendanceWindow
from registration.window import RegisterWindow

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("モード選択")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        btn_attendance = QPushButton("出席モードを起動")
        btn_attendance.clicked.connect(self.launch_attendance)

        btn_register = QPushButton("登録モードを起動")
        btn_register.clicked.connect(self.launch_register)

        layout.addWidget(btn_attendance)
        layout.addWidget(btn_register)
        self.setLayout(layout)

    def launch_attendance(self):
        self.attendance_window = AttendanceWindow()
        self.attendance_window.show()

    def launch_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()