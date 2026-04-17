from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
from contextlib import asynccontextmanager

from stage1.database import create_db, get_profile_by_id, get_profile_by_name, get_all_profiles, delete_profile_by_id, create_profile
from stage1.models import CreateProfileRequest
from stage1.utils import fetch_external_apis, classify_profile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    create_db()
    logger.info("Database initialized succesfully")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Profile Classification API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware BEFORE defining routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/profiles")
async def create_or_get_profile(request: CreateProfileRequest):
    """Create a new profile or return existing one if name already exists."""
    try:
        # Validate name
        if not request.name or not request.name.strip():
            raise HTTPException(
                status_code=400,
                detail="Name cannot be empty"
            )
        
        name = request.name.strip()
        
        # Check if profile already exists
        existing = get_profile_by_name(name)
        
        if existing:
            return {
                "status": "success",
                "message": "Profile already exists",
                "data": {
                    "id": str(existing.id),
                    "name": existing.name,
                    "gender": existing.gender,
                    "gender_probability": existing.gender_probability,
                    "sample_size": existing.sample_size,
                    "age": existing.age,
                    "age_group": existing.age_group,
                    "country_id": existing.country_id,
                    "country_probability": existing.country_probability,
                    "created_at": existing.created_at.isoformat() + "Z"
                }
            }
        
        # Fetch from external APIs
        api_response = await fetch_external_apis(name)
        
        # Classify and extract data
        classified_data = classify_profile(name, api_response)
        
        # Save to database
        new_profile = create_profile(classified_data)
        
        return {
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
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/api/profiles/{id}")
async def get_single_profile(id: str):
    """Get a single profile by ID."""
    try:
        profile = get_profile_by_id(id)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        return {
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
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/api/profiles")
async def get_profiles_list(
    gender: Optional[str] = Query(None),
    country_id: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None)
):
    """Get all profiles with optional filtering. Query parameters are case-insensitive."""
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
        
        return {
            "status": "success",
            "count": len(profile_list),
            "data": profile_list
        }
    except Exception as e:
        logger.error(f"Error fetching profiles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.delete("/api/profiles/{id}")
async def delete_profile(id: str):
    """Delete a profile by ID."""
    try:
        deleted = delete_profile_by_id(id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        # Return 204 No Content
        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "Profile Classification API is healthy"
    }