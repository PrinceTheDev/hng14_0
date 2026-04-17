from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from contextlib import asynccontextmanager

from stage1.database import (
    create_db,
    get_profile_by_id,
    get_profile_by_name,
    get_all_profiles,
    delete_profile_by_id,
    create_profile
)
from stage1.models import CreateProfileRequest
from stage1.utils import fetch_external_apis, classify_profile

# setting up logging for the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create databse table on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    logger.info("Database initialized succesfully")
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="Profile API",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/api/profiles", status_code=201)
async def create_or_get_profile(request: CreateProfileRequest):
    """Create a new profile or return an existing one if it name already exists."""

    try:
        if not request.name or not request.name.strip():
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Name cannot be empty"}
            )
        
        name = request.name.strip()
        existing_profile = get_profile_by_name(name)

        if existing_profile:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Profile already exists",
                    "data": {
                        "id": str(existing_profile.id),
                        "name": existing_profile.name,
                        "gender": existing_profile.gender,
                        "gender_probability": existing_profile.gender_probability,
                        "sample_size": existing_profile.sample_size,
                        "age": existing_profile.age,
                        "age_group": existing_profile.age_group,
                        "country_id": existing_profile.country_id,
                        "country_probability": existing_profile.country_probability,
                        "created_at": existing_profile.created_at.isoformat() + "Z"
                    }
                }
            )
        
        api_response = await fetch_external_apis(name)

        classified_data = classify_profile(name, api_response)

        new_profile = create_profile(classified_data)

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "data": {
                    "id": str(new_profile.id),
                    "name": new_profile.name,
                    "gender": new_profile.gender,
                    "gender_probability": new_profile.gender_probability,
                    "sample_size": new_profile.sample_size,
                    "age": new_profile.age,
                    "age_group": new_profile.age_group,
                    "country_id": new_profile.country_id,
                    "country_probability": new_profile.country_probability,
                    "created_at": new_profile.created_at.isoformat() + "Z"
                }
            }
        )
    
    except Exception as e:
        logger.error(f"Error creating profile: str{e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )
    

@app.get("/api/profiles/{id}")
async def get_single_profile(id: str):
    try:
        profile = get_profile_by_id(id)

        if not profile:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "Profile not found"
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": {
                    "id": str(profile.id),
                    "name": profile.name,
                    "gender": profile.gender,
                    "gender_probability": profile.gender_probability,
                    "sample_size": profile.sample_size,
                    "age": profile.age,
                    "age_group": profile.age_group,
                    "country_id": profile.country_id,
                    "country_probability": profile.country_probability,
                    "created_at": profile.created_at.isoformat() + "Z"
                }
            }
        )
    
    except Exception as e:
        logger.error(f"Error fetching profile by id: str{e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )


@app.get("/api/profiles")
async def get_profiles_list(
    gender: Optional[str] = Query(None),
    country_id: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None)
):

    try:
        profiles = get_all_profiles(gender, country_id, age_group)

        profile_list = []
        for profile in profiles:
            profile_list.append({
                "id": str(profile.id),
                "name": profile.name,
                "gender": profile.gender,
                "age": profile.age,
                "age_group": profile.age_group,
                "country_id": profile.country_id
            })

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "count": len(profile_list),
                "data": profile_list
            }
        )
    
    except Exception as e:
        logger.error(f"Error fetching profiles list: str{e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )
    


@app.delete("/api/profiles/{id}")
async def delete_profile(id: str):

    try:

        deleted = delete_profile_by_id(id)

        if not deleted:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "Profile not found"
                }
            )
        
        return JSONResponse(
            status_code=204,
            content=None
        )
    
    except Exception as e:
        logger.error(f"Error deleting profile: str{e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )
    

@app.get("/api/health")
async def health_check():
    return {
        "status": "success",
        "message": "API is healthy"
    }