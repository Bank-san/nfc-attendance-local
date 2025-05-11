from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QDateTimeEdit, QSpinBox, QLineEdit
)
from PyQt6.QtCore import QDateTime, QTime, QDate
from datetime import datetime
from sqlmodel import Session
from database.engine import engine
from database.models import Attendance

class ManualEntryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手動来館記録")
        self.resize(1000, 600)

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["名前（かな）", "年齢", "入室", "退室"])
        layout.addWidget(self.table)

        button_row = QHBoxLayout()
        self.add_row_button = QPushButton("+ 行を追加")
        self.add_row_button.clicked.connect(self.add_row)
        self.save_button = QPushButton("一括保存")
        self.save_button.clicked.connect(self.save_all)
        button_row.addWidget(self.add_row_button)
        button_row.addWidget(self.save_button)
        layout.addLayout(button_row)

        self.setLayout(layout)
        self.add_row()  # 最初に1行表示

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        name_item = QLineEdit()
        self.table.setCellWidget(row, 0, name_item)

        age_item = QSpinBox()
        age_item.setRange(0, 120)
        self.table.setCellWidget(row, 1, age_item)

        current_time = QTime.currentTime()
        today = QDate.currentDate()

        in_time = QDateTimeEdit()
        in_time.setDate(today)
        in_time.setTime(current_time)
        in_time.setDisplayFormat("HH:mm")
        in_time.setCalendarPopup(False)
        self.table.setCellWidget(row, 2, in_time)

        out_time = QDateTimeEdit()
        out_time.setDate(today)
        out_time.setTime(current_time)
        out_time.setDisplayFormat("HH:mm")
        out_time.setCalendarPopup(False)
        self.table.setCellWidget(row, 3, out_time)

    def save_all(self):
        now_str = datetime.now().strftime("%Y%m%d")
        today = QDate.currentDate().toPyDate()
        saved = 0

        with Session(engine) as session:
            for row in range(self.table.rowCount()):
                name_widget = self.table.cellWidget(row, 0)
                age_widget = self.table.cellWidget(row, 1)
                in_widget = self.table.cellWidget(row, 2)
                out_widget = self.table.cellWidget(row, 3)

                name = name_widget.text().strip()
                age = age_widget.value()
                in_time = in_widget.time().toPyTime()
                out_time = out_widget.time().toPyTime()

                check_in = datetime.combine(today, in_time)
                check_out = datetime.combine(today, out_time)

                if not name:
                    continue  # 名前未入力はスキップ

                manual_uid = f"manual-{now_str}-{row+1:03d}"
                attendance = Attendance(
                    nfc_id=manual_uid,
                    check_in=check_in,
                    check_out=check_out,
                    snapshot_name_kanji="",
                    snapshot_name_kana=name,
                    snapshot_emergency_contact="",
                    snapshot_date_of_birth="",
                    snapshot_school="",
                    snapshot_prefecture="",
                    snapshot_city="",
                    snapshot_block="",
                    snapshot_building="",
                    snapshot_gender="",
                    snapshot_additional_info=f"年齢: {age}"
                )
                session.add(attendance)
                saved += 1
            session.commit()

        QMessageBox.information(self, "保存完了", f"{saved}件の来館記録を保存しました。")
        self.close()
