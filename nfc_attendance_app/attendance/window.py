from database.engine import engine
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt
from attendance.nfc_worker import NFCWorker
from database.models import User, Attendance
from sqlmodel import Session, select
from datetime import datetime
from registration.window import RegisterWindow
import os

class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("出席管理")
        self.resize(500, 300)

        # 背景画像の設定
        palette = QPalette()
        bg_path = os.path.join(os.path.dirname(__file__), "..", "images", "background.png")
        palette.setBrush(self.backgroundRole(), QBrush(QPixmap(bg_path)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # メインレイアウト
        layout = QVBoxLayout()

        # NFCアイコン表示
        self.nfc_icon = QLabel()
        nfc_path = os.path.join(os.path.dirname(__file__), "..", "images", "NFC.gif")
        self.nfc_icon.setPixmap(QPixmap(nfc_path).scaledToWidth(100))
        self.nfc_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.nfc_icon)

        # ステータスラベル
        self.label = QLabel("↓ カードをかざしてください")
        self.label.setFont(QFont("Arial", 18))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: gray;")
        layout.addWidget(self.label)

        # 登録ボタン
        self.register_button = QPushButton("新規登録")
        self.register_button.setStyleSheet("padding: 8px; font-size: 16px;")
        self.register_button.clicked.connect(self.open_register_window)
        layout.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        # NFCワーカー起動
        self.worker = NFCWorker()
        self.worker.signal.connect(self.process_uid)
        self.worker.start()

    def process_uid(self, uid):
        if uid == "カードをかざしてください":
            self.label.setText("↓ カードをかざしてください")
            self.label.setStyleSheet("color: gray; font-size: 16px;")
            return

        if uid.startswith("エラー") or not uid:
            self.label.setText("⚠️ 読み取りエラー")
            self.label.setStyleSheet("color: red; font-size: 16px;")
            return

        with Session(engine) as session:
            user = session.exec(select(User).where(User.nfc_id == uid)).first()
            if not user:
                self.label.setText("未登録のカードです。登録してください。")
                self.label.setStyleSheet("color: orange; font-size: 16px;")
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
                self.label.setText(f"👋 おつかれさまでした、{user.name_kanji} さん")
                self.label.setStyleSheet("color: red; font-size: 16px;")
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
                self.label.setText(f"🙌 ようこそ、{user.name_kanji} さん")
                self.label.setStyleSheet("color: green; font-size: 16px;")

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
