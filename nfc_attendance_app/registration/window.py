from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from registration.logic import is_registered, register_user, get_user_by_uid
from attendance.nfc_worker import NFCWorker

class RegisterWindow(QWidget):
    def __init__(self, attendance_window=None):
        super().__init__()
        self.attendance_window = attendance_window
        if self.attendance_window:
            self.attendance_window.pause_worker()
            print("[DEBUG] RegisterWindow: attendance paused")

        self.setWindowTitle("カード登録フォーム")
        self.setMinimumWidth(500)

        self.layout = QFormLayout()

        self.name_kanji_input = QLineEdit()
        self.name_kana_input = QLineEdit()
        self.dob_input = QLineEdit()
        self.emergency_input = QLineEdit()
        self.school_input = QLineEdit()
        self.pref_input = QLineEdit()
        self.city_input = QLineEdit()
        self.block_input = QLineEdit()
        self.building_input = QLineEdit()
        self.gender_input = QLineEdit()
        self.additional_input = QLineEdit()

        self.nfc_id_input = QLineEdit()
        self.nfc_id_input.setPlaceholderText("カードをかざしてください...")
        self.nfc_id_input.setReadOnly(True)
        self.nfc_id_input.setStyleSheet("background-color: #eee; color: #555;")

        self.status_label = QLabel("カードをかざしてください")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")

        self.layout.addRow("名前（漢字）", self.name_kanji_input)
        self.layout.addRow("名前（かな）", self.name_kana_input)
        self.layout.addRow("生年月日（yyyymmdd）", self.dob_input)
        self.layout.addRow("緊急連絡先", self.emergency_input)
        self.layout.addRow("学校名", self.school_input)
        self.layout.addRow("都道府県", self.pref_input)
        self.layout.addRow("市町村", self.city_input)
        self.layout.addRow("番地", self.block_input)
        self.layout.addRow("建物名", self.building_input)
        self.layout.addRow("性別", self.gender_input)
        self.layout.addRow("その他", self.additional_input)
        self.layout.addRow("NFCカードID", self.nfc_id_input)
        self.layout.addRow(self.status_label)

        self.submit_button = QPushButton("登録")
        self.submit_button.clicked.connect(self.on_submit)
        self.layout.addRow(self.submit_button)

        self.setLayout(self.layout)

        self.reader = NFCWorker(wait_seconds=0)
        self.reader.signal.connect(self.on_uid_detected)
        self.reader.start()

        self.last_uid = None

    def on_uid_detected(self, uid):
        if uid != self.last_uid:
            self.last_uid = uid
            self.nfc_id_input.setText(uid)
            if is_registered(uid):
                user = get_user_by_uid(uid)
                self.name_kanji_input.setText(user.name_kanji)
                self.name_kana_input.setText(user.name_kana)
                self.dob_input.setText(user.date_of_birth)
                self.emergency_input.setText(user.emergency_contact)
                self.school_input.setText(user.school)
                self.pref_input.setText(user.prefecture)
                self.city_input.setText(user.city)
                self.block_input.setText(user.block)
                self.building_input.setText(user.building)
                self.gender_input.setText(user.gender)
                self.additional_input.setText(user.additional_info)

                self.status_label.setText("⚠️ このカードはすでに登録されています")
                self.status_label.setStyleSheet("color: orange;")
            else:
                self.status_label.setText("新規カードが読み取られました")
                self.status_label.setStyleSheet("color: green;")

    def on_submit(self):
        uid = self.nfc_id_input.text().strip()
        if not uid:
            self.status_label.setText("⚠️ カードをかざしてください")
            self.status_label.setStyleSheet("color: red;")
            return

        user_data = {
            "name_kanji": self.name_kanji_input.text(),
            "name_kana": self.name_kana_input.text(),
            "date_of_birth": self.dob_input.text(),
            "emergency_contact": self.emergency_input.text(),
            "school": self.school_input.text(),
            "prefecture": self.pref_input.text(),
            "city": self.city_input.text(),
            "block": self.block_input.text(),
            "building": self.building_input.text(),
            "gender": self.gender_input.text(),
            "additional_info": self.additional_input.text(),
        }

        if is_registered(uid):
            self.status_label.setText("⚠️ このカードはすでに登録されています")
            self.status_label.setStyleSheet("color: red;")
            return

        register_user(uid, **user_data)
        self.status_label.setText("✅ 登録が完了しました")
        self.status_label.setStyleSheet("color: green;")
        QTimer.singleShot(1200, self.close)

    def closeEvent(self, event):
        if self.attendance_window:
            self.attendance_window.resume_attendance_mode()
            print("[DEBUG] RegisterWindow: attendance resumed")
        super().closeEvent(event)
