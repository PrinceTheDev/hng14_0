from pydantic import BaseModel, Field
from typing import Optional, List



"""Create a Profile table in the database"""
class CreateProfileRequest(BaseModel):
    name: str = Field(..., min_length=1)


class ProfileResponse(BaseModel):
    id: str
    name: str
    gender: str
    gender_probability: float
    sample_size: int
    age: int
    age_group: str
    country_id: str
    country_probability: float
    created_at: str


class ProfileListItem(BaseModel):
    id: str
    name: str
    gender: str
    age: int
    age_group: str
    country_id: str