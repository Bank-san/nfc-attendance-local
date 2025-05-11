from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from sqlalchemy import Column

class Attendance(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  # ← これを追加
    id: Optional[int] = Field(default=None, primary_key=True)
    nfc_id: str
    check_in: datetime
    check_out: Optional[datetime] = None
    remarks: Optional[str] = None

class User(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  # ← これも追加
    id: Optional[int] = Field(default=None, primary_key=True)
    nfc_id: str
    name: str
    emergency_contact: str
    date_of_birth: str
    school: str
    address: str
    gender: str
    additional_info: str


import sys
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReaderWindow()
    window.show()
    sys.exit(app.exec())
