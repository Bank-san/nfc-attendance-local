# nfc_attendance_app/init_db.py
from sqlmodel import SQLModel
from database.engine import engine
from database.models import User, Attendance  # ← 必ず明示的に import！

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
    print("✅ DB作成完了")
