from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import Attendance
from database import get_session
from datetime import datetime

router = APIRouter()

@router.post("/attendance")
def check_in(attendance: Attendance, session: Session = Depends(get_session)):
    # NFCカードIDの当日分を取得
    today = datetime.now().date()
    existing = session.exec(
        select(Attendance)
        .where(Attendance.nfc_id == attendance.nfc_id)
        .where(Attendance.check_in >= datetime.combine(today, datetime.min.time()))
    ).first()

    now = datetime.now()
    if existing and not existing.check_out:
        existing.check_out = now
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return {"status": "checked out", "record": existing}
    else:
        new_attendance = Attendance(nfc_id=attendance.nfc_id, check_in=now)
        session.add(new_attendance)
        session.commit()
        session.refresh(new_attendance)
        return {"status": "checked in", "record": new_attendance}
