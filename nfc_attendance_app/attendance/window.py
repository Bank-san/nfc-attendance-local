from database.engine import engine
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont
from attendance.nfc_worker import NFCWorker
from database.models import User, Attendance
from sqlmodel import Session, select
from datetime import datetime
from registration.window import RegisterWindow

class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("出席管理")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("↓ カードをかざしてください")
        self.label.setFont(QFont("Arial", 16))
        layout.addWidget(self.label)

        self.register_button = QPushButton("新規登録")
        self.register_button.clicked.connect(self.open_register_window)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.worker = NFCWorker()
        self.worker.signal.connect(self.process_uid)
        self.worker.start()

    def process_uid(self, uid):
        if uid == "カードをかざしてください":
            self.label.setText("↓ カードをかざしてください")
            return

        if uid.startswith("エラー") or not uid:
            return

        with Session(engine) as session:
            user = session.exec(select(User).where(User.nfc_id == uid)).first()
            if not user:
                self.label.setText("未登録のカードです。登録してください。")
                return

            latest = session.exec(
                select(Attendance)
                .where(Attendance.nfc_id == uid)
                .order_by(Attendance.check_in.desc())
            ).first()

            if latest and latest.check_out is None:
                latest.check_out = datetime.now()
                session.add(latest)
                session.commit()
                self.label.setText(f"おつかれさまでした、{user.name_kanji} さん")
            else:
                new_att = Attendance(
                    nfc_id=uid,
                    check_in=datetime.now(),
                    snapshot_name_kanji=user.name_kanji,
                    snapshot_name_kana=user.name_kana,
                    snapshot_emergency_contact=user.emergency_contact,
                    snapshot_date_of_birth=user.date_of_birth,
                    snapshot_school=user.school,
                    snapshot_prefecture=user.prefecture,
                    snapshot_city=user.city,
                    snapshot_block=user.block,
                    snapshot_building=user.building,
                    snapshot_gender=user.gender,
                    snapshot_additional_info=user.additional_info,
                )
                session.add(new_att)
                session.commit()
                self.label.setText(f"ようこそ、{user.name_kanji} さん")

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
