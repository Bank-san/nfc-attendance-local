from sqlmodel import Session, select
from database.models import User
from database.engine import engine

def is_registered(uid: str) -> bool:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.nfc_id == uid)).first()
        return user is not None

def register_user(uid: str, name: str, dob: str):
    with Session(engine) as session:
        user = User(nfc_id=uid, name=name, date_of_birth=dob)
        session.add(user)
        session.commit()