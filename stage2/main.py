from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional

from stage2.database import create_db, get_all_profiles_filtered, get_profile_by_id
from stage2.models import GetAllProfilesResponse, SearchResponse, ErrorResponse, ProfileListResponse
from stage2.utils import parse_natural_language_query, validate_filter_params



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    logger.info("Database created successfully")
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="Intelligence Query Engine System",
    version="1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)



@app.get("/api/profiles")
async def get_profiles(
    gender: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    country_id: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None, ge=0, le=150),
    max_age: Optional[int] = Query(None, ge=0, le=150),
    min_gender_probability: Optional[float] = Query(None, ge=0, le=1),
    min_country_probability: Optional[float] = Query(None, ge=0, le=1),
    sort_by: str = Query("created_at", pattern="^(age|created_at|gender_probability)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
):
    
    is_valid, error_msg = validate_filter_params(
        gender=gender,
        age_group=age_group,
        country_id=country_id,
        min_age=min_age,
        max_age=max_age,
        min_gender_probability=min_gender_probability,
        min_country_probability=min_country_probability,
        sort_by=sort_by,
        order=order,
    )

    if not is_valid:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": error_msg}
        )
    
    limit = min(limit, 50)
    

    profiles, total = get_all_profiles_filtered(
        gender=gender,
        age_group=age_group,
        country_id=country_id,
        min_age=min_age,
        max_age=max_age,
        min_gender_probability=min_gender_probability,
        min_country_probability=min_country_probability,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit,
    )

    data = [
        {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "gender_probability": p.gender_probability,
            "age": p.age,
            "age_group": p.age_group,
            "country_id": p.country_id,
            "country_name": p.country_name,
            "country_probability": p.country_probability,
            "created_at": p.created_at.isoformat() + "Z" if p.created_at.tzinfo else p.created_at.isoformat() + "Z",
        }
        for p in profiles
    ]


    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "data": data
        }
    )



@app.get("/api/profiles/search")
async def search_profiles(
    q: str = Query(..., min_length=1, description="Natural language query"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
):
    
    if not q or not q.strip():
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing or empty query"}
        )
    
    filters = parse_natural_language_query(q)
    
    if filters is None:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Unable to interpret query"}
        )
    
    limit = min(limit, 50)
    
    gender = filters.get("gender")
    age_group = filters.get("age_group")
    country_id = filters.get("country_id")
    min_age = filters.get("min_age")
    max_age = filters.get("max_age")


    profiles, total = get_all_profiles_filtered(
        gender=gender,
        age_group=age_group,
        country_id=country_id,
        min_age=min_age,
        max_age=max_age,
        sort_by="created_at",
        order="asc",
        page=page,
        limit=limit,
    )


    data = [
        {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "gender_probability": p.gender_probability,
            "age": p.age,
            "age_group": p.age_group,
            "country_id": p.country_id,
            "country_name": p.country_name,
            "country_probability": p.country_probability,
            "created_at": p.created_at.isoformat() + "Z" if p.created_at.tzinfo else p.created_at.isoformat() + "Z",
        }
        for p in profiles
    ]


    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "query": q,
            "filters_applied": filters,
            "data": data
        }
    )