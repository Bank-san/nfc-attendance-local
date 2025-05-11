# nfc_attendance_app/database/engine.py

from sqlmodel import create_engine, SQLModel

# SQLiteのローカルDBファイルを使用
DATABASE_URL = "sqlite:///nfc_attendance.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

print("▶ 使用中のDB:", DATABASE_URL)

