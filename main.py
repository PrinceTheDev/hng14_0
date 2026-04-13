from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import httpx
import logging


#setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# create fastapi app
app = FastAPI(
    title="Gender Classification API",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def validate_name(name: Optional[str]) -> str:

    if name is None:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Missing required parameter: name"
            }
        )

    if not name.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Name parameter cannot be empty"
            }
        )

    return name.strip()


async def fetch_from_genderize(name: str) -> dict:

    url = "https://api.genderize.io"
    params = {"name": name}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail={
                "status": "error",
                "message": "External API timeout"
            }
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=502,
            details={
                "status": "error",
                "message": "External API error"
            }
        )
    

def process_genderize_response(name: str, data: dict) -> Optional[dict]:
    """Process and validate the Genderize API response"""

    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count", 0)

    if gender is None or count == 0:
        return None
    
    is_confident = (probability >= 0.7) and (count >= 100)

    processed_at = datetime.utcnow().isoformat() + "Z"

    return {
        "name": name,
        "gender": gender,
        "probability": probability,
        "sample_size": count,
        "is_confident": is_confident,
        "processed_at": processed_at
    }

@app.get("/api/classify")
async def classify_name(name: Optional[str] = Query(None)):

    validated_name = validate_name(name)

    data = await fetch_from_genderize(validated_name)

    processed_data = process_genderize_response(validated_name, data)

    if processed_data is None:
        raise HTTPException(
            status_code=200,
            detail={
                "status": "error",
                "message": "No prediction available for the provided name"
            }
        )
    
    return {
        "status": "success",
        "data": processed_data
    }


@app.get("/health")
def read_root():
    return {
        "status": "running",
        "message": "Gender Classification API is healthy"
    }