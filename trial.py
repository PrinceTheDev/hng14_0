from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import datetime
from typing import Optional
import httpx
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Test API",
    version="1.0.0"
)

# origins = [
#     "http://localhost:3000",       # React default
#     "http://127.0.0.1:3000",
#     "https://yourdomain.com",      # Production domain
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # Can use ["*"] for public APIs (not recommended for production)
    allow_credentials=True,        # Allow cookies/auth headers
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],           # Allow all headers
)


def validate_name(name: Optional[str]) -> str:
    if name is None:
        raise HTTPException(
            status_code=400,
            details={
                "status": "error",
                "message": "Name required"
            },
        )
    
    if not name.strip():
        raise HTTPException(
            status_code=400,
            details={
                "status": "error",
                "message": "Name cannot be empty"
            },
        )
    
    return name.strip()


async def fetch_genderize_api(name: str) -> dict:

    url = f"https://api.genderize.io?name={name}"
    params = {"name": name}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            details={
                "status": "error",
                "message": "External API request timed out"
            }
        )

def process_genderize_api(name: str, data: dict) -> dict:
    
    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count", 0)

    if gender is None or count == 0:
        return None

