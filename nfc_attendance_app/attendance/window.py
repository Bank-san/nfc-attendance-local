from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont, QMovie
from PyQt6.QtCore import Qt, QSize, Qt as QtCore, QTimer
import os

from attendance.nfc_worker import NFCWorker
from database.engine import engine
from database.models import User, Attendance
from sqlmodel import Session, select
from datetime import datetime

class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.illustrations = []
        self.illustrations_drawn = False
        self.setWindowTitle("Attendifyy 出席画面")
        self.showFullScreen()

        # 背景画像設定
        palette = QPalette()
        bg_path = os.path.join(os.path.dirname(__file__), "..", "images", "background.png")
        palette.setBrush(self.backgroundRole(), QBrush(QPixmap(bg_path)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # メインフレーム
        self.frame = QFrame()
        self.frame.setObjectName("MainFrame")
        self.setStyleSheet("""
            QFrame#MainFrame {
                background-color: rgba(100, 100, 100, 0.35);
                border: 3px solid orange;
                border-radius: 24px;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)

        self.frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 中央の内容レイアウト
        self.frame_layout = QVBoxLayout()
        self.frame_layout.setContentsMargins(60, 60, 60, 60)
        self.frame_layout.setSpacing(30)

        gif_path = os.path.join(os.path.dirname(__file__), "..", "images", "NFC.gif")
        self.nfc_icon = QLabel()
        self.movie = QMovie(gif_path)
        self.nfc_icon.setMovie(self.movie)
        self.nfc_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie.start()
        self.frame_layout.addWidget(self.nfc_icon)

        self.label = QLabel("カードをタップしてください")
        self.label.setFont(QFont("Arial", 28, weight=QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #fff;")
        self.frame_layout.addWidget(self.label)

        self.frame.setLayout(self.frame_layout)

        # メインレイアウト中央寄せ
        self.main_layout = QVBoxLayout()
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.main_layout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(self.main_layout)

        # NFCリーダー起動
        self.worker = NFCWorker()
        self.worker.signal.connect(self.process_uid)
        self.worker.start()

    def showEvent(self, event):
        super().showEvent(event)
        if not self.illustrations_drawn:
            self._add_corner_illustrations()
            self.illustrations_drawn = True

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if hasattr(self, "frame"):
            screen_width = self.width()
            self.frame.setFixedWidth(int(screen_width * 0.4))

        illustration_size = int(self.width() * 0.12)
        for icon, pixmap, dx, dy, align in self.illustrations:
            scaled = pixmap.scaled(
                illustration_size, illustration_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon.setPixmap(scaled)
            x, y = self._pos_from_alignment(align, dx, dy, illustration_size)
            icon.setGeometry(x, y, illustration_size, illustration_size)

        if hasattr(self, "movie"):
            size = int(self.width() * 0.08)
            self.movie.setScaledSize(QSize(size, size))

    def _add_corner_illustrations(self):
        for name, dx, dy, align in [
            ("Drone.png", 20, 20, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft),
            ("gaming.png", -20, 20, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight),
            ("vrbox.png", 20, -20, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft),
            ("services.png", -20, -20, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight),
        ]:
            path = os.path.join(os.path.dirname(__file__), "..", "images", name)
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"\u26a0\ufe0f 読み込み失敗: {path}")
                continue

            icon = QLabel(self)
            icon.setStyleSheet("background: transparent;")
            icon.setScaledContents(False)
            icon.show()
            self.illustrations.append((icon, pixmap, dx, dy, align))

    def _pos_from_alignment(self, align, dx, dy, size):
        w, h = self.width(), self.height()
        x = dx if align & Qt.AlignmentFlag.AlignLeft else w - size + dx
        y = dy if align & Qt.AlignmentFlag.AlignTop else h - size + dy
        return x, y

    def reset_message(self):
        self.label.setText("カードをタップしてください")
        self.label.setStyleSheet("color: #fff; font-size: 28px;")

    def process_uid(self, uid):
        if not uid or uid in ["", "カードをかざしてください"]:
            self.reset_message()
            return

        if uid.startswith("エラー"):
            self.label.setText("\u26a0\ufe0f カード読み取りエラー")
            self.label.setStyleSheet("color: red; font-size: 28px;")
            QTimer.singleShot(5000, self.reset_message)
            return

        with Session(engine) as session:
            user = session.exec(select(User).where(User.nfc_id == uid)).first()
            if not user:
                self.label.setText("未登録のカードです")
                self.label.setStyleSheet("color: orange; font-size: 28px;")
                QTimer.singleShot(5000, self.reset_message)
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
                self.label.setText(f"\ud83d\udc4b おつかれさまでした、{user.name_kanji} さん")
                self.label.setStyleSheet("color: red; font-size: 28px;")
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
                self.label.setText(f"\ud83d\ude4c ようこそ、{user.name_kanji} さん")
                self.label.setStyleSheet("color: green; font-size: 28px;")

        # 一定時間後に初期メッセージに戻す
        QTimer.singleShot(5000, self.reset_message)