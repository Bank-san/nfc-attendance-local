from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox
)
from PyQt6.QtGui import QFont
from sqlmodel import Session
from database import engine
from models import User

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("カード登録")
        self.resize(400, 400)

        layout = QVBoxLayout()

        title = QLabel("新規利用者登録")
        title.setFont(QFont("Arial", 16))
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.nfc_input = QLineEdit()
        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.dob_input = QLineEdit()
        self.school_input = QLineEdit()
        self.address_input = QLineEdit()
        self.gender_input = QLineEdit()
        self.additional_input = QLineEdit()

        form_layout.addRow("NFC ID", self.nfc_input)
        form_layout.addRow("名前", self.name_input)
        form_layout.addRow("緊急連絡先", self.contact_input)
        form_layout.addRow("生年月日 (YYYY-MM-DD)", self.dob_input)
        form_layout.addRow("学校名", self.school_input)
        form_layout.addRow("住所", self.address_input)
        form_layout.addRow("性別", self.gender_input)
        form_layout.addRow("その他（持病やアレルギーなど）", self.additional_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("登録")
        self.submit_button.clicked.connect(self.register_user)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def register_user(self):
        with Session(engine) as session:
            nfc_id = self.nfc_input.text().strip()

            # すでに登録済みか確認
            existing = session.exec(
                session.query(User).filter(User.nfc_id == nfc_id)
            ).first()

            if existing:
                QMessageBox.warning(self, "エラー", "このカードはすでに登録されています。")
                return

            user = User(
                nfc_id=nfc_id,
                name=self.name_input.text(),
                emergency_contact=self.contact_input.text(),
                date_of_birth=self.dob_input.text(),
                school=self.school_input.text(),
                address=self.address_input.text(),
                gender=self.gender_input.text(),
                additional_info=self.additional_input.text()
            )
            session.add(user)
            session.commit()

            QMessageBox.information(self, "成功", "登録が完了しました。")
            self.close()
