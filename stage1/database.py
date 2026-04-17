from sqlmodel import SQLModel, create_engine, Session, Field, select
from uuid6 import uuid7
from datetime import datetime, timezone
from typing import Optional
import logging


logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./profiles.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)



class Profile(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    gender: str
    gender_probability: float
    sample_size: int
    age: int
    age_group: str
    country_id: str
    country_probability: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


def create_profile(profile_data: dict) -> Profile:
    profile = Profile(
        id=str(uuid7()),
        name=profile_data["name"],
        gender=profile_data["gender"],
        gender_probability=profile_data["gender_probability"],
        sample_size=profile_data["sample_size"],
        age=profile_data["age"],
        age_group=profile_data["age_group"],
        country_id=profile_data["country_id"],
        country_probability=profile_data["country_probability"],
        created_at=datetime.now(timezone.utc)
    )
    with Session(engine) as session:
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile


def get_profile_by_id(profile_id: str) -> Optional[Profile]:
    with Session(engine) as session:
        return session.get(Profile, profile_id)
    

def get_profile_by_name(name: str) -> Optional[Profile]:
    with Session(engine) as session:
        statement = select(Profile).where(Profile.name.ilike(name))
        return session.exec(statement).first()
    
def get_all_profiles(
        gender: Optional[str] = None,
        country_id: Optional[str] = None,
        age_group: Optional[str] = None,
) -> list:
    with Session(engine) as session:
        statement = select(Profile)


        if gender:
            statement = statement.where(Profile.gender.ilike(gender))

        if country_id:
            statement = statement.where(Profile.country_id.ilike(country_id))

        if age_group:
            statement = statement.where(Profile.age_group.ilike(age_group))

        return session.exec(statement).all()
    

def delete_profile_by_id(profile_id: str) -> bool:
    with Session(engine) as session:
        profile = session.get(Profile, profile_id)
        if profile:
            session.delete(profile)
            session.commit()
            return True
    return False