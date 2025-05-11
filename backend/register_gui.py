from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from sqlmodel import Session
from database import engine
from models import User

from smartcard.System import readers
from smartcard.util import toHexString
import time


class NFCReaderThread(QThread):
    nfc_detected = pyqtSignal(str)

    def run(self):
        r = readers()
        if not r:
            self.nfc_detected.emit("⚠️ リーダー未接続")
            return

        reader = r[0]
        connection = reader.createConnection()

        while True:
            try:
                print("[DEBUG] Waiting for card...")
                connection.connect()
                cmd = [0xff, 0xca, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(cmd)

                if sw1 == 0x90 and sw2 == 0x00:
                    uid = toHexString(data)
                    print(f"[DEBUG] Card detected: {uid}")
                    self.nfc_detected.emit(uid)

                connection.disconnect()
            except Exception as e:
                print(f"[DEBUG] Exception: {e}")
                self.nfc_detected.emit(f"エラー: {e}")
            self.msleep(1000)


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("カード登録フォーム")
        self.setMinimumWidth(400)

        self.layout = QFormLayout()

        self.name_input = QLineEdit()
        self.emergency_input = QLineEdit()
        self.dob_input = QLineEdit()
        self.school_input = QLineEdit()
        self.address_input = QLineEdit()
        self.gender_input = QLineEdit()
        self.additional_input = QLineEdit()
        self.nfc_id_input = QLineEdit()
        self.nfc_id_input.setPlaceholderText("カードをかざしてください...")
        self.nfc_id_input.setReadOnly(True)
        self.nfc_id_input.setStyleSheet("background-color: #eee; color: #555;")

        self.layout.addRow("名前", self.name_input)
        self.layout.addRow("緊急連絡先", self.emergency_input)
        self.layout.addRow("生年月日 (YYYY-MM-DD)", self.dob_input)
        self.layout.addRow("学校名", self.school_input)
        self.layout.addRow("住所", self.address_input)
        self.layout.addRow("性別", self.gender_input)
        self.layout.addRow("その他（持病やアレルギーなど）", self.additional_input)
        self.layout.addRow("NFCカードID", self.nfc_id_input)

        self.submit_button = QPushButton("登録")
        self.submit_button.clicked.connect(self.register_user)
        self.layout.addRow(self.submit_button)

        self.setLayout(self.layout)

        self.reader_thread = NFCReaderThread()
        self.reader_thread.nfc_detected.connect(self.set_nfc_id)
        self.reader_thread.start()

    def set_nfc_id(self, uid):
        print(f"[DEBUG] set_nfc_id() called with: {uid}")
        if uid.startswith("エラー") or "リーダー" in uid:
            QMessageBox.warning(self, "NFC エラー", uid)
        else:
            self.nfc_id_input.setText(uid)

    def register_user(self):
        if not self.nfc_id_input.text().strip():
            QMessageBox.warning(self, "未入力", "カードをかざしてNFC IDを取得してください。")
            return

        user = User(
            nfc_id=self.nfc_id_input.text().strip(),
            name=self.name_input.text().strip(),
            emergency_contact=self.emergency_input.text().strip(),
            date_of_birth=self.dob_input.text().strip(),
            school=self.school_input.text().strip(),
            address=self.address_input.text().strip(),
            gender=self.gender_input.text().strip(),
            additional_info=self.additional_input.text().strip(),
        )

        with Session(engine) as session:
            session.add(user)
            session.commit()

        QMessageBox.information(self, "成功", "登録が完了しました。")
        self.close()
