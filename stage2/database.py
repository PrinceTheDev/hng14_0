import os
from sqlmodel import SQLModel, Field, create_engine, Session, select
from uuid6 import uuid7
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/profile.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


class Profile(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    gender: str = Field(index=True)
    gender_probability: float
    age: int = Field(index=True)
    age_group: str = Field(index=True)
    country_id: str = Field(index=True)
    country_name: str
    country_probability: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


def create_db():
    SQLModel.metadata.create_all(engine)


def get_profile_by_id(profile_id: str) -> Optional[Profile]:
    with Session(engine) as session:
        return session.get(Profile, profile_id)


def get_profile_by_name(name: str) -> Optional[Profile]:
    with Session(engine) as session:
        query = select(Profile).where(Profile.name.ilike(name))
        return session.exec(query).first()


def create_profile(profile_data: dict) -> Profile:
    with Session(engine) as session:
        profile = Profile(
            id=str(uuid7()),
            name=profile_data["name"],
            gender=profile_data["gender"],
            gender_probability=profile_data["gender_probability"],
            age=profile_data["age"],
            age_group=profile_data["age_group"],
            country_id=profile_data["country_id"],
            country_name=profile_data["country_name"],
            country_probability=profile_data["country_probability"],
            created_at=datetime.now(timezone.utc)
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile


def get_all_profiles_filtered(
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    country_id: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_gender_probability: Optional[float] = None,
    min_country_probability: Optional[float] = None,
    sort_by: str = "created_at",
    order: str = "asc",
    page: int = 1,
    limit: int = 10,
) -> tuple[list[Profile], int]:
    """Get paginated and filtered profiles"""
    
    page = max(page, 1)
    limit = min(max(limit, 1), 50)
    
    with Session(engine) as session:
        query = select(Profile)
        
        # Apply filters
        if gender:
            query = query.where(Profile.gender.ilike(gender))
        if age_group:
            query = query.where(Profile.age_group.ilike(age_group))
        if country_id:
            query = query.where(Profile.country_id.ilike(country_id))
        if min_age is not None:
            query = query.where(Profile.age >= min_age)
        if max_age is not None:
            query = query.where(Profile.age <= max_age)
        if min_gender_probability is not None:
            query = query.where(Profile.gender_probability >= min_gender_probability)
        if min_country_probability is not None:
            query = query.where(Profile.country_probability >= min_country_probability)
        
        # Get total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()
        
        # Apply sorting
        sort_map = {
            "age": Profile.age,
            "created_at": Profile.created_at,
            "gender_probability": Profile.gender_probability,
        }
        sort_column = sort_map.get(sort_by, Profile.created_at)
        
        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (page - 1) * limit
        profiles = session.exec(query.offset(offset).limit(limit)).all()
        
        return profiles, total