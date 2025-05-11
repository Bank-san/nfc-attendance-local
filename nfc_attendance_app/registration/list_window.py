from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QFileDialog
)
from sqlmodel import Session, select
from database.engine import engine
from database.models import User
import csv


class UserListWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登録者リスト")
        self.resize(1000, 600)

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "UID", "名前（漢字）", "名前（かな）", "緊急連絡先", "生年月日", "学校名",
            "都道府県", "市町村", "番地", "建物名", "性別", "その他"
        ])
        layout.addWidget(self.table)

        button_row = QHBoxLayout()
        self.reload_button = QPushButton("再読み込み")
        self.reload_button.clicked.connect(self.load_users)

        self.save_button = QPushButton("編集内容を保存")
        self.save_button.clicked.connect(self.save_users)

        self.export_button = QPushButton("CSVとして保存")
        self.export_button.clicked.connect(self.export_csv)

        self.import_button = QPushButton("CSVから読み込み")
        self.import_button.clicked.connect(self.import_csv)

        button_row.addWidget(self.reload_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.export_button)
        button_row.addWidget(self.import_button)
        layout.addLayout(button_row)

        self.setLayout(layout)
        self.load_users()

    def load_users(self):
        with Session(engine) as session:
            self.users = session.exec(select(User)).all()

        self.table.setRowCount(len(self.users))
        for row, user in enumerate(self.users):
            self.table.setItem(row, 0, QTableWidgetItem(user.nfc_id))
            self.table.setItem(row, 1, QTableWidgetItem(user.name_kanji))
            self.table.setItem(row, 2, QTableWidgetItem(user.name_kana))
            self.table.setItem(row, 3, QTableWidgetItem(user.emergency_contact))
            self.table.setItem(row, 4, QTableWidgetItem(user.date_of_birth))
            self.table.setItem(row, 5, QTableWidgetItem(user.school))
            self.table.setItem(row, 6, QTableWidgetItem(user.prefecture))
            self.table.setItem(row, 7, QTableWidgetItem(user.city))
            self.table.setItem(row, 8, QTableWidgetItem(user.block))
            self.table.setItem(row, 9, QTableWidgetItem(user.building))
            self.table.setItem(row, 10, QTableWidgetItem(user.gender))
            self.table.setItem(row, 11, QTableWidgetItem(user.additional_info))

    def save_users(self):
        with Session(engine) as session:
            for row, original in enumerate(self.users):
                user = session.exec(select(User).where(User.nfc_id == original.nfc_id)).first()
                if user:
                    user.name_kanji = self.table.item(row, 1).text()
                    user.name_kana = self.table.item(row, 2).text()
                    user.emergency_contact = self.table.item(row, 3).text()
                    user.date_of_birth = self.table.item(row, 4).text()
                    user.school = self.table.item(row, 5).text()
                    user.prefecture = self.table.item(row, 6).text()
                    user.city = self.table.item(row, 7).text()
                    user.block = self.table.item(row, 8).text()
                    user.building = self.table.item(row, 9).text()
                    user.gender = self.table.item(row, 10).text()
                    user.additional_info = self.table.item(row, 11).text()
            session.commit()
        QMessageBox.information(self, "保存完了", "編集内容を保存しました。")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "CSVファイルを保存", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "UID", "名前（漢字）", "名前（かな）", "緊急連絡先", "生年月日", "学校名",
                    "都道府県", "市町村", "番地", "建物名", "性別", "その他"
                ])
                for row in range(self.table.rowCount()):
                    row_data = [
                        self.table.item(row, col).text() if self.table.item(row, col) else ""
                        for col in range(12)
                    ]
                    writer.writerow(row_data)
            QMessageBox.information(self, "保存完了", "CSVファイルを保存しました。")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSVファイルを開く", "", "CSV Files (*.csv)")
        if path:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                with Session(engine) as session:
                    for row in reader:
                        uid = row["UID"]
                        user = session.exec(select(User).where(User.nfc_id == uid)).first()
                        if user:
                            user.name_kanji = row["名前（漢字）"]
                            user.name_kana = row["名前（かな）"]
                            user.emergency_contact = row["緊急連絡先"]
                            user.date_of_birth = row["生年月日"]
                            user.school = row["学校名"]
                            user.prefecture = row["都道府県"]
                            user.city = row["市町村"]
                            user.block = row["番地"]
                            user.building = row["建物名"]
                            user.gender = row["性別"]
                            user.additional_info = row["その他"]
                        else:
                            session.add(User(
                                nfc_id=uid,
                                name_kanji=row["名前（漢字）"],
                                name_kana=row["名前（かな）"],
                                emergency_contact=row["緊急連絡先"],
                                date_of_birth=row["生年月日"],
                                school=row["学校名"],
                                prefecture=row["都道府県"],
                                city=row["市町村"],
                                block=row["番地"],
                                building=row["建物名"],
                                gender=row["性別"],
                                additional_info=row["その他"]
                            ))
                    session.commit()
            QMessageBox.information(self, "読み込み完了", "CSVの内容を登録しました。")
            self.load_users()
