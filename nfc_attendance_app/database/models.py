from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nfc_id: str
    name_kanji: str
    name_kana: str
    emergency_contact: str
    date_of_birth: str
    school: str
    prefecture: str  # 都道府県
    city: str        # 市町村
    block: str       # 番地
    building: str    # 建物名
    gender: str
    additional_info: str

class Attendance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nfc_id: str
    check_in: datetime
    check_out: Optional[datetime] = None

    # スナップショット情報（記録時点のユーザー情報）
    snapshot_name_kanji: str
    snapshot_name_kana: str
    snapshot_emergency_contact: str
    snapshot_date_of_birth: str
    snapshot_school: str
    snapshot_prefecture: str
    snapshot_city: str
    snapshot_block: str
    snapshot_building: str
    snapshot_gender: str
    snapshot_additional_info: str