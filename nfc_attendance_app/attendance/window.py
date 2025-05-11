from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal
from .nfc_worker import NFCWorker
from database.models import User, Attendance
from sqlmodel import Session, select
from datetime import datetime

class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("出席管理")
        self.resize(400, 150)

        layout = QVBoxLayout()

        self.label = QLabel("\u2193 カードをかざしてください")
        self.label.setFont(QFont("Arial", 16))
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.worker = NFCWorker()
        self.worker.signal.connect(self.process_uid)
        self.worker.start()

    def process_uid(self, uid):
        if uid.startswith("エラー"):
            self.label.setText(uid)
            return

        with Session(engine) as session:
            user = session.exec(select(User).where(User.nfc_id == uid)).first()
            if not user:
                self.label.setText("未登録のカードです。登録してください。")
                return

            latest = session.exec(
                select(Attendance).where(Attendance.nfc_id == uid).order_by(Attendance.check_in.desc())
            ).first()

            if latest and latest.check_out is None:
                latest.check_out = datetime.now()
                session.add(latest)
                session.commit()
                self.label.setText(f"おつかれさまでした、{user.name} さん")
            else:
                new_att = Attendance(nfc_id=uid, check_in=datetime.now())
                session.add(new_att)
                session.commit()
                self.label.setText(f"ようこそ、{user.name} さん")