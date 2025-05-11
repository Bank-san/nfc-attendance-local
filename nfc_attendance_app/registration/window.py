from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QMessageBox
from registration.logic import is_registered, register_user
from attendance.nfc_worker import NFCWorker

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("カード登録フォーム")
        self.setMinimumWidth(400)

        self.layout = QFormLayout()

        self.name_input = QLineEdit()
        self.dob_input = QLineEdit()
        self.nfc_id_input = QLineEdit()
        self.nfc_id_input.setPlaceholderText("カードをかざしてください...")
        self.nfc_id_input.setReadOnly(True)
        self.nfc_id_input.setStyleSheet("background-color: #eee; color: #555;")

        self.layout.addRow("名前", self.name_input)
        self.layout.addRow("生年月日", self.dob_input)
        self.layout.addRow("NFCカードID", self.nfc_id_input)

        self.submit_button = QPushButton("登録")
        self.submit_button.clicked.connect(self.on_submit)
        self.layout.addRow(self.submit_button)

        self.setLayout(self.layout)

        self.reader = NFCWorker()
        self.reader.signal.connect(self.on_uid_detected)
        self.reader.start()

    def on_uid_detected(self, uid):
        if is_registered(uid):
            QMessageBox.information(self, "確認", "このカードはすでに登録されています")
        else:
            self.nfc_id_input.setText(uid)

    def on_submit(self):
        uid = self.nfc_id_input.text().strip()
        name = self.name_input.text().strip()
        dob = self.dob_input.text().strip()
        if not uid or not name:
            QMessageBox.warning(self, "未入力", "名前とUIDが必要です")
            return
        register_user(uid, name, dob)
        QMessageBox.information(self, "完了", "ユーザー登録が完了しました")
        self.close()
