import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QTextEdit, QMessageBox, QFormLayout
)
from PyQt6.QtCore import QDate
from sqlmodel import Session, SQLModel, create_engine
from models import User
import datetime

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)
SQLModel.metadata.create_all(engine)

class UserRegistrationForm(QWidget):
    def __init__(self, uid):
        super().__init__()
        self.setWindowTitle("利用者登録")
        self.uid = uid
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.uid_input = QLineEdit(self.uid)
        self.uid_input.setReadOnly(True)
        layout.addRow("UID (自動):", self.uid_input)

        self.name_input = QLineEdit()
        layout.addRow("名前:", self.name_input)

        self.emergency_input = QLineEdit()
        layout.addRow("緊急連絡先:", self.emergency_input)

        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        layout.addRow("生年月日:", self.dob_input)

        self.school_input = QLineEdit()
        layout.addRow("学校:", self.school_input)

        self.address_input = QLineEdit()
        layout.addRow("住所:", self.address_input)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["男性", "女性", "その他"])
        layout.addRow("性別:", self.gender_input)

        self.additional_input = QTextEdit()
        layout.addRow("その他（持病やアレルギーなど）:", self.additional_input)

        self.submit_button = QPushButton("登録")
        self.submit_button.clicked.connect(self.register_user)
        layout.addRow(self.submit_button)

        self.setLayout(layout)

    def register_user(self):
        try:
            user = User(
                nfc_id=self.uid_input.text(),
                name=self.name_input.text(),
                emergency_contact=self.emergency_input.text(),
                date_of_birth=self.dob_input.date().toString("yyyy-MM-dd"),
                school=self.school_input.text(),
                address=self.address_input.text(),
                gender=self.gender_input.currentText(),
                additional_info=self.additional_input.toPlainText()
            )
            with Session(engine) as session:
                session.add(user)
                session.commit()
            QMessageBox.information(self, "成功", "利用者情報を登録しました！")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"登録に失敗しました: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    uid = "01 2E 4C E3 50 18 56 73"  # テスト用UID（NFC側から渡すようにする）
    window = UserRegistrationForm(uid)
    window.show()
    sys.exit(app.exec())
