import httpx
from fastapi import HTTPException
import logging


logger = logging.getLogger(__name__)

async def fetch_external_apis(name: str) -> dict:
    """
    We fetch data from Genderize, Agify and Nationalize APIs.
    Returns a combined response or raises HTTPException with a 502 status
    """

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            genderize_url = f"https://api.genderize.io?name={name}"
            agify_url = f"https://api.agify.io?name={name}"
            nationalize_url = f"https://api.nationalize.io?name={name}"
            
            responses = await client.get(genderize_url), \
                        await client.get(agify_url), \
                        await client.get(nationalize_url)
            
            genderize_response = responses[0].json()
            agify_response = responses[1].json()
            nationalize_response = responses[2].json()

            return {
                "genderize": genderize_response,
                "agify": agify_response,
                "nationalize": nationalize_response
            }
    except Exception as e:
        logger.error(f"Error fetching external APIs: {e}")
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch data from external APIs"
        )
    

def classify_profile(name: str, api_response: dict) -> dict:
    genderize = api_response.get("genderize", {})
    agify = api_response.get("agify", {})
    nationalize = api_response.get("nationalize", {})

    gender = genderize.get("gender")
    gender_probability = genderize.get("probability")
    sample_size = genderize.get("count", 0)

    if gender is None or sample_size == 0 or gender_probability is None:
        raise HTTPException(
            status_code=502,
            detail="Invalid response from Genderize API"
        )
    
    age = agify.get("age")
    if age is None:
        raise HTTPException(
            status_code=502,
            detail="Invalid response from Agify API"
        )
    

    countries = nationalize.get("country", [])
    if not countries or len(countries) == 0:
        raise HTTPException(
            status_code=502,
            detail="Invalid response from Nationalize API"
        )
    
    age_group = classify_age(age)

    top_country = max(countries, key=lambda x: x["probability"])
    country_id = top_country.get("country_id")
    country_probability = top_country.get("probability")

    return {
        "name": name,
        "gender": gender,
        "gender_probability": gender_probability,
        "sample_size": sample_size,
        "age": age,
        "age_group": age_group,
        "country_id": country_id,
        "country_probability": country_probability
    }


def classify_age(age: int) -> str:
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    else:
        return "senior"
