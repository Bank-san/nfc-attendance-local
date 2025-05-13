from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont, QMovie
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
from datetime import datetime
from attendance.nfc_worker import NFCWorker
from database.engine import engine
from database.models import User, Attendance
from sqlmodel import Session, select
from registration.window import RegisterWindow

class AttendanceWindow(QWidget):
    def pause_worker(self):
        if self.worker.isRunning():
            self.worker.mode = "idle"
            print("[DEBUG] worker paused (mode=idle)")
    def resume_attendance_mode(self):
        self.worker.mode = "attendance"
        if not self.worker.isRunning():
            self.worker.start()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("受付システム")
        

        # NFCWorker は明示的に起動する
        self.worker = NFCWorker(mode="attendance")
        self.worker.signal.connect(self.handle_signal)

        self.player_in = QMediaPlayer()
        self.audio_in = QAudioOutput()
        self.player_in.setAudioOutput(self.audio_in)
        self.player_in.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), "..", "sounds", "in.mp3")))

        self.player_out = QMediaPlayer()
        self.audio_out = QAudioOutput()
        self.player_out.setAudioOutput(self.audio_out)
        self.player_out.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), "..", "sounds", "out.mp3")))

        palette = QPalette()
        bg_path = os.path.join(os.path.dirname(__file__), "..", "images", "background.png")
        palette.setBrush(self.backgroundRole(), QBrush(QPixmap(bg_path)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

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

        self.main_layout = QVBoxLayout()
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.main_layout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(self.main_layout)

        self.illustrations = []
        self._add_corner_illustrations()

    def _add_corner_illustrations(self):
        corners = [
            ("Drone.png", 20, 20, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft),
            ("gaming.png", -20, 20, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight),
            ("vrbox.png", 20, -20, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft),
            ("services.png", -20, -20, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight),
        ]
        for name, dx, dy, align in corners:
            path = os.path.join(os.path.dirname(__file__), "..", "images", name)
            pixmap = QPixmap(path)
            if pixmap.isNull():
                continue
            icon = QLabel(self)
            icon.setPixmap(pixmap)
            icon.setStyleSheet("background: transparent;")
            icon.setScaledContents(True)
            icon.show()
            self.illustrations.append((icon, dx, dy, align))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "illustrations"):
            return
        size = min(int(self.width() * 0.16), 200)
        for icon, dx, dy, align in self.illustrations:
            icon.setFixedSize(size, size)
            x = dx if align & Qt.AlignmentFlag.AlignLeft else self.width() - size - abs(dx)
            y = dy if align & Qt.AlignmentFlag.AlignTop else self.height() - size - abs(dy)
            icon.move(x, y)

    def handle_signal(self, uid):
        if self.worker.mode != "attendance":
            return
        self.process_uid(uid)

    def process_uid(self, uid):
        if not uid or uid in ["", "カードをかざしてください"]:
            self.reset_message()
            return
        if uid.startswith("エラー"):
            self.label.setText("⚠️ カード読み取りエラー")
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
                self.label.setText(f"👋 おつかれさまでした、{user.name_kanji} さん")
                self.label.setStyleSheet("color: red; font-size: 28px;")
                self.player_out.play()
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
                self.label.setStyleSheet("color: green; font-size: 28px;")
                self.player_in.play()

        QTimer.singleShot(5000, self.reset_message)

    def reset_message(self):
        self.label.setText("カードをタップしてください")
        self.label.setStyleSheet("color: #fff; font-size: 28px;")
