from sqlmodel import Session, select
from database.models import User
from database.engine import engine

def is_registered(uid: str) -> bool:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.nfc_id == uid)).first()
        return user is not None

def register_user(
    nfc_id: str,
    name_kanji: str,
    name_kana: str,
    emergency_contact: str,
    date_of_birth: str,
    school: str,
    prefecture: str,
    city: str,
    block: str,
    building: str,
    gender: str,
    additional_info: str
):
    user = User(
        nfc_id=nfc_id,
        name_kanji=name_kanji,
        name_kana=name_kana,
        emergency_contact=emergency_contact,
        date_of_birth=date_of_birth,
        school=school,
        prefecture=prefecture,
        city=city,
        block=block,
        building=building,
        gender=gender,
        additional_info=additional_info
    )
    with Session(engine) as session:
        session.add(user)
        session.commit()


def get_user_by_uid(uid: str) -> User:
    with Session(engine) as session:
        return session.exec(select(User).where(User.nfc_id == uid)).first()

def update_user(
    uid: str,
    name: str,
    emergency_contact: str,
    date_of_birth: str,
    school: str,
    prefecture: str,
    city: str,
    block: str,
    building: str,
    gender: str,
    additional_info: str
):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.nfc_id == uid)).first()
        if user:
            user.name = name
            user.emergency_contact = emergency_contact
            user.date_of_birth = date_of_birth
            user.school = school
            user.prefecture = prefecture
            user.city = city
            user.block = block
            user.building = building
            user.gender = gender
            user.additional_info = additional_info
            session.add(user)
            session.commit()

def delete_user(uid: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.nfc_id == uid)).first()
        if user:
            session.delete(user)
            session.commit()
