from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class CreateProfileRequest(BaseModel):
    name: str = Field(..., min_length=1, description="The name of the profile")


class ProfileListResponse(BaseModel):
    id: str
    name: str
    gender: str
    gender_probability: float
    age: int
    age_group: str
    country_id: str
    country_name: str
    country_probability: float
    created_at: datetime

    class Config:
        from_attributes = True


class GetAllProfilesResponse(BaseModel):
    status: str = "success"
    page: int
    page_size: int
    total: int
    data: list[ProfileListResponse]


class SearchResponse(BaseModel):
    status: str = "success"
    page: int
    page_size: int
    total: int
    query: str
    filters_applied: dict
    data: list[ProfileListResponse]


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str