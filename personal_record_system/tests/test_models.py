from sqlalchemy.orm import Session

from personal_record_system.app.db import Base, SessionLocal, engine
from personal_record_system.app.models import Person


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_person_model_defaults():
    session: Session = SessionLocal()
    try:
        person = Person(external_id="abc123", full_name="John Doe", email="john@example.com", source="test")
        session.add(person)
        session.commit()
        session.refresh(person)

        assert person.id is not None
        assert person.created_at is not None
        assert person.updated_at is not None
    finally:
        session.close()
