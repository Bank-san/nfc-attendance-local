from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QDateEdit, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QRadioButton, QButtonGroup
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.rcParams['font.family'] = 'Noto Sans JP'

from datetime import datetime, timedelta
from sqlmodel import Session, select
from database.engine import engine
from database.models import User, Attendance
from collections import Counter

class AttendanceSummaryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("来場者分析ダッシュボード")
        self.setMinimumSize(1000, 700)

        layout = QVBoxLayout()
        control_row = QHBoxLayout()

        self.today_radio = QRadioButton("今日")
        self.week_radio = QRadioButton("今週")
        self.month_radio = QRadioButton("今月")
        self.fiscal_radio = QRadioButton("今年度")
        self.custom_radio = QRadioButton("カスタム")
        self.today_radio.setChecked(True)

        self.range_group = QButtonGroup()
        for btn in [self.today_radio, self.week_radio, self.month_radio, self.fiscal_radio, self.custom_radio]:
            self.range_group.addButton(btn)
            control_row.addWidget(btn)

        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyyMMdd")
        self.end_date.setDisplayFormat("yyyyMMdd")
        today = datetime.today().date()
        self.start_date.setDate(today)
        self.end_date.setDate(today)
        control_row.addWidget(QLabel("開始日:"))
        control_row.addWidget(self.start_date)
        control_row.addWidget(QLabel("終了日:"))
        control_row.addWidget(self.end_date)

        self.reload_button = QPushButton("再読み込み")
        self.reload_button.clicked.connect(self.reload_all)
        control_row.addWidget(self.reload_button)

        layout.addLayout(control_row)

        self.tabs = QTabWidget()
        self.tab_widgets = {
            "来場者数": self.create_tab_canvas(),
            "年齢別": self.create_tab_canvas(),
            "学年別": self.create_tab_canvas(),
            "市町村別": self.create_tab_canvas(),
            "性別別": self.create_tab_canvas(),
            "曜日別": self.create_tab_canvas(),
            "時間帯別": self.create_tab_canvas(),
            "出席ログ": QWidget()
        }

        for name, widget in self.tab_widgets.items():
            self.tabs.addTab(widget, name)

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.reload_all()

    def create_tab_canvas(self):
        canvas = FigureCanvas(Figure())
        wrapper = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        wrapper.setLayout(layout)
        canvas.axes = canvas.figure.subplots()
        return wrapper

    def get_selected_range(self):
        today = datetime.today()
        if self.today_radio.isChecked():
            start = datetime(today.year, today.month, today.day)
            end = start + timedelta(days=1)
        elif self.week_radio.isChecked():
            start = today - timedelta(days=today.weekday())
            start = datetime(start.year, start.month, start.day)
            end = start + timedelta(days=7)
        elif self.month_radio.isChecked():
            start = datetime(today.year, today.month, 1)
            if today.month == 12:
                end = datetime(today.year + 1, 1, 1)
            else:
                end = datetime(today.year, today.month + 1, 1)
        elif self.fiscal_radio.isChecked():
            start = datetime(today.year if today.month >= 4 else today.year - 1, 4, 1)
            end = datetime(start.year + 1, 4, 1)
        else:
            start = datetime.combine(self.start_date.date().toPyDate(), datetime.min.time())
            end = datetime.combine(self.end_date.date().toPyDate(), datetime.max.time())
        return start, end

    def get_uids_and_records(self):
        start, end = self.get_selected_range()
        with Session(engine) as session:
            records = session.exec(
                select(Attendance).where(Attendance.check_in >= start, Attendance.check_in <= end)
            ).all()
            uids = set(r.nfc_id for r in records)
        return uids, records

    def reload_all(self):
        self.plot_total()
        self.plot_age()
        self.plot_grade()
        self.plot_city()
        self.plot_gender()
        self.plot_weekday()
        self.plot_hour()
        self.show_table()

    def plot_total(self):
        canvas = self.tab_widgets["来場者数"].layout().itemAt(0).widget()
        uids, _ = self.get_uids_and_records()
        ax = canvas.axes
        ax.clear()
        ax.bar(["来場者数"], [len(uids)])
        ax.set_ylim(0, max(10, len(uids) + 5))
        canvas.draw()

    def plot_age(self):
        canvas = self.tab_widgets["年齢別"].layout().itemAt(0).widget()
        today = datetime.today()
        uids, _ = self.get_uids_and_records()
        counter = Counter()
        with Session(engine) as session:
            for uid in uids:
                user = session.exec(select(User).where(User.nfc_id == uid)).first()
                if user and user.date_of_birth:
                    try:
                        birth = datetime.strptime(user.date_of_birth, "%Y-%m-%d")
                        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
                        counter[str(age)] += 1
                    except:
                        pass
        ax = canvas.axes
        ax.clear()
        ages = sorted(counter.items(), key=lambda x: int(x[0]))
        labels = [a[0] for a in ages]
        values = [a[1] for a in ages]
        ax.bar(labels, values)
        canvas.draw()

    def plot_grade(self):
        canvas = self.tab_widgets["学年別"].layout().itemAt(0).widget()
        uids, _ = self.get_uids_and_records()
        counter = Counter()
        with Session(engine) as session:
            for uid in uids:
                user = session.exec(select(User).where(User.nfc_id == uid)).first()
                if user and user.date_of_birth:
                    try:
                        birth = datetime.strptime(user.date_of_birth, "%Y-%m-%d")
                        school_year_base = datetime(datetime.today().year, 4, 1)
                        age = school_year_base.year - birth.year - ((school_year_base.month, school_year_base.day) < (birth.month, birth.day))
                        if 6 <= age <= 11:
                            grade = f"小{age - 5}"
                        elif 12 <= age <= 14:
                            grade = f"中{age - 11}"
                        elif 15 <= age <= 17:
                            grade = f"高{age - 14}"
                        else:
                            grade = "その他"
                        counter[grade] += 1
                    except:
                        pass
        ax = canvas.axes
        ax.clear()
        order = [f"小{i}" for i in range(1, 7)] + [f"中{i}" for i in range(1, 4)] + [f"高{i}" for i in range(1, 4)] + ["その他"]
        values = [counter.get(k, 0) for k in order]
        ax.bar(order, values)
        canvas.draw()

    def plot_city(self):
        canvas = self.tab_widgets["市町村別"].layout().itemAt(0).widget()
        uids, _ = self.get_uids_and_records()
        counter = Counter()
        with Session(engine) as session:
            for uid in uids:
                user = session.exec(select(User).where(User.nfc_id == uid)).first()
                if user and user.city:
                    counter[user.city] += 1
        ax = canvas.axes
        ax.clear()
        ax.bar(counter.keys(), counter.values())
        ax.set_xticklabels(counter.keys(), rotation=45, ha='right')
        canvas.draw()

    def plot_gender(self):
        canvas = self.tab_widgets["性別別"].layout().itemAt(0).widget()
        uids, _ = self.get_uids_and_records()
        counter = Counter()
        with Session(engine) as session:
            for uid in uids:
                user = session.exec(select(User).where(User.nfc_id == uid)).first()
                if user and user.gender:
                    counter[user.gender] += 1
        ax = canvas.axes
        ax.clear()
        ax.pie(counter.values(), labels=counter.keys(), autopct='%1.1f%%')
        canvas.draw()

    def plot_weekday(self):
        canvas = self.tab_widgets["曜日別"].layout().itemAt(0).widget()
        base = datetime.today().date()
        start = datetime.combine(base - timedelta(days=6), datetime.min.time())
        end = datetime.combine(base + timedelta(days=1), datetime.max.time())
        with Session(engine) as session:
            records = session.exec(
                select(Attendance).where(Attendance.check_in >= start, Attendance.check_in <= end)
            ).all()
        counter = Counter()
        seen = set()
        for r in records:
            key = (r.nfc_id, r.check_in.date())
            if key not in seen:
                counter[r.check_in.strftime("%a")] += 1
                seen.add(key)
        order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ax = canvas.axes
        ax.clear()
        ax.bar(order, [counter.get(d, 0) for d in order])
        canvas.draw()

    def plot_hour(self):
        canvas = self.tab_widgets["時間帯別"].layout().itemAt(0).widget()
        _, records = self.get_uids_and_records()
        counter = Counter()
        for r in records:
            counter[r.check_in.hour] += 1
        ax = canvas.axes
        ax.clear()
        ax.bar(range(24), [counter.get(h, 0) for h in range(24)])
        ax.set_xticks(range(24))
        canvas.draw()

    def show_table(self):
        widget = self.tab_widgets["出席ログ"]
        layout = QVBoxLayout()
        table = QTableWidget()
        _, records = self.get_uids_and_records()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["UID", "入室", "退室"])
        table.setRowCount(len(records))
        for i, r in enumerate(records):
            table.setItem(i, 0, QTableWidgetItem(r.nfc_id))
            table.setItem(i, 1, QTableWidgetItem(str(r.check_in)))
            table.setItem(i, 2, QTableWidgetItem(str(r.check_out) if r.check_out else ""))
        layout.addWidget(table)
        widget.setLayout(layout)
