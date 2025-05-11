import sys
import time
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont

from smartcard.System import readers
from smartcard.util import toHexString

from sqlmodel import Session
from database import engine
from models import Attendance
from register_gui import RegisterWindow

class NFCWorker(QThread):
    signal = pyqtSignal(str)

    def run(self):
        r = readers()
        if not r:
            self.signal.emit("⚠️ NFCリーダーが見つかりません")
            return

        reader = r[0]
        connection = reader.createConnection()

        while True:
            try:
                self.signal.emit("カードをかざしてください...")
                connection.connect()
                cmd = [0xff, 0xca, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(cmd)

                if sw1 == 0x90 and sw2 == 0x00:
                    uid = toHexString(data)
                    self.signal.emit(f"UID: {uid}")
                    self.save_attendance(uid)
                else:
                    self.signal.emit(f"UID取得失敗: {sw1} {sw2}")

                time.sleep(1)
                connection.disconnect()

            except Exception as e:
                self.signal.emit(f"エラー: {e}")
                time.sleep(0.5)

    def save_attendance(self, uid):
        now = datetime.now()
        with Session(engine) as session:
            attendance = Attendance(nfc_id=uid, check_in=now)
            session.add(attendance)
            session.commit()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFC 出席記録")
        self.resize(400, 150)

        layout = QVBoxLayout()

        self.label = QLabel("\u2193 スタートを押してください")
        self.label.setFont(QFont("Arial", 16))
        layout.addWidget(self.label)

        self.button = QPushButton("読み取り開始")
        self.register_button = QPushButton("カード登録")
        self.register_button.clicked.connect(self.open_register_window)

        button_row = QHBoxLayout()
        button_row.addWidget(self.button)
        button_row.addWidget(self.register_button)
        layout.addLayout(button_row)

        self.button.clicked.connect(self.start_reading)

        self.setLayout(layout)
        self.worker = NFCWorker()
        self.worker.signal.connect(self.update_label)

    def start_reading(self):
        self.worker.start()
        self.button.setEnabled(False)

    def update_label(self, message):
        self.label.setText(message)

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
