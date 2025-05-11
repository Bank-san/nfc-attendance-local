from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QDateEdit, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog
)
from PyQt6.QtCore import QDate
from sqlmodel import Session, select
from database.engine import engine
from database.models import Attendance
from datetime import datetime, timedelta
import csv


class AttendanceHistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("出席履歴")
        self.setMinimumSize(1200, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.filter_type_group = QButtonGroup()

        self.filter_row = QHBoxLayout()
        self.today_radio = QRadioButton("今日")
        self.week_radio = QRadioButton("今週")
        self.month_radio = QRadioButton("今月")
        self.fiscal_radio = QRadioButton("今年度")
        self.custom_radio = QRadioButton("カスタム")

        self.filter_type_group.addButton(self.today_radio)
        self.filter_type_group.addButton(self.week_radio)
        self.filter_type_group.addButton(self.month_radio)
        self.filter_type_group.addButton(self.fiscal_radio)
        self.filter_type_group.addButton(self.custom_radio)

        self.today_radio.setChecked(True)

        for btn in [self.today_radio, self.week_radio, self.month_radio, self.fiscal_radio, self.custom_radio]:
            self.filter_row.addWidget(btn)

        self.layout.addLayout(self.filter_row)

        self.date_row = QHBoxLayout()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        today = QDate.currentDate()
        self.start_date.setDate(today)
        self.end_date.setDate(today)
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)
        self.date_row.addWidget(QLabel("開始日:"))
        self.date_row.addWidget(self.start_date)
        self.date_row.addWidget(QLabel("終了日:"))
        self.date_row.addWidget(self.end_date)
        self.layout.addLayout(self.date_row)
        self.date_row.setEnabled(False)

        self.search_row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("名前で検索（漢字 or ひらがな）")
        self.uid_input = QLineEdit()
        self.uid_input.setPlaceholderText("UIDで検索")
        self.search_row.addWidget(QLabel("🔍"))
        self.search_row.addWidget(self.name_input)
        self.search_row.addWidget(self.uid_input)
        self.layout.addLayout(self.search_row)

        self.reload_button = QPushButton("再読み込み")
        self.reload_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.reload_button)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.export_button = QPushButton("CSVとして保存")
        self.export_button.clicked.connect(self.export_csv)
        self.layout.addWidget(self.export_button)

        self.filter_type_group.buttonClicked.connect(self.toggle_date_row)
        self.load_data()

    def toggle_date_row(self):
        self.date_row.setEnabled(self.custom_radio.isChecked())

    def load_data(self):
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        today_end = today_start + timedelta(days=1)

        if self.today_radio.isChecked():
            start, end = today_start, today_end
        elif self.week_radio.isChecked():
            start = today_start - timedelta(days=today_start.weekday())
            end = today_end
        elif self.month_radio.isChecked():
            start = datetime(now.year, now.month, 1)
            end = datetime(now.year + (now.month == 12), (now.month % 12) + 1, 1)
        elif self.fiscal_radio.isChecked():
            fiscal_start = datetime(now.year if now.month >= 4 else now.year - 1, 4, 1)
            fiscal_end = datetime(fiscal_start.year + 1, 4, 1)
            start, end = fiscal_start, fiscal_end
        elif self.custom_radio.isChecked():
            start = datetime.combine(self.start_date.date().toPyDate(), datetime.min.time())
            end = datetime.combine(self.end_date.date().toPyDate(), datetime.max.time())
        else:
            start, end = today_start, today_end

        name_filter = self.name_input.text().strip().lower()
        uid_filter = self.uid_input.text().strip().lower()

        with Session(engine) as session:
            records = session.exec(
                select(Attendance).where(
                    Attendance.check_in >= start,
                    Attendance.check_in <= end
                ).order_by(Attendance.check_in.desc())
            ).all()

            filtered_results = []
            for record in records:
                kanji = record.snapshot_name_kanji.lower()
                kana = record.snapshot_name_kana.lower()
                if name_filter and name_filter not in kanji and name_filter not in kana:
                    continue
                if uid_filter and uid_filter not in record.nfc_id.lower():
                    continue
                filtered_results.append(record)

            self.table.setColumnCount(14)
            self.table.setHorizontalHeaderLabels([
                "名前（漢字）", "名前（ひらがな）", "UID", "緊急連絡先", "生年月日", "学校名",
                "都道府県", "市町村", "番地", "建物名", "性別", "その他", "入室", "退室"
            ])
            self.table.setRowCount(len(filtered_results))

            for row, record in enumerate(filtered_results):
                self.table.setItem(row, 0, QTableWidgetItem(record.snapshot_name_kanji))
                self.table.setItem(row, 1, QTableWidgetItem(record.snapshot_name_kana))
                self.table.setItem(row, 2, QTableWidgetItem(record.nfc_id))
                self.table.setItem(row, 3, QTableWidgetItem(record.snapshot_emergency_contact))
                self.table.setItem(row, 4, QTableWidgetItem(record.snapshot_date_of_birth))
                self.table.setItem(row, 5, QTableWidgetItem(record.snapshot_school))
                self.table.setItem(row, 6, QTableWidgetItem(record.snapshot_prefecture))
                self.table.setItem(row, 7, QTableWidgetItem(record.snapshot_city))
                self.table.setItem(row, 8, QTableWidgetItem(record.snapshot_block))
                self.table.setItem(row, 9, QTableWidgetItem(record.snapshot_building))
                self.table.setItem(row, 10, QTableWidgetItem(record.snapshot_gender))
                self.table.setItem(row, 11, QTableWidgetItem(record.snapshot_additional_info))
                self.table.setItem(row, 12, QTableWidgetItem(str(record.check_in)))
                self.table.setItem(row, 13, QTableWidgetItem(str(record.check_out) if record.check_out else ""))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "CSVファイルを保存", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "名前（漢字）", "名前（ひらがな）", "UID", "緊急連絡先", "生年月日", "学校名",
                    "都道府県", "市町村", "番地", "建物名", "性別", "その他", "入室", "退室"
                ])
                for row in range(self.table.rowCount()):
                    row_data = [
                        self.table.item(row, col).text() if self.table.item(row, col) else ""
                        for col in range(14)
                    ]
                    writer.writerow(row_data)
