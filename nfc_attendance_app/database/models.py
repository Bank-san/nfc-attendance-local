from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nfc_id: str
    name: str
    date_of_birth: str

class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nfc_id: str
    check_in: datetime
    check_out: Optional[datetime] = None