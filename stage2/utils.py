import re
import logging
from typing import Optional, Dict, List


logger = logging.getLogger(__name__)


COUNTRY_MAP = {
    "nigeria": "NG", "ghana": "GH", "kenya": "KE", "tanzania": "TZ",
    "uganda": "UG", "south africa": "ZA", "egypt": "EG", "ethiopia": "ET",
    "cameroon": "CM", "senegal": "SN", "benin": "BJ", "côte d'ivoire": "CI",
    "cote d'ivoire": "CI", "ivory coast": "CI", "mali": "ML", "burkina faso": "BF",
    "guinea": "GN", "liberia": "LR", "sierra leone": "SL", "togo": "TG",
    "niger": "NE", "chad": "TD", "sudan": "SD", "gabon": "GA",
    "congo": "CG", "drc": "CD", "democratic republic of congo": "CD",
    "angola": "AO", "zambia": "ZM", "zimbabwe": "ZW", "botswana": "BW",
    "namibia": "NA", "lesotho": "LS", "mauritius": "MU", "seychelles": "SC",
    "united states": "US", "usa": "US", "uk": "GB", "united kingdom": "GB",
    "canada": "CA", "australia": "AU", "india": "IN", "china": "CN",
    "japan": "JP", "germany": "DE", "france": "FR", "italy": "IT",
    "spain": "ES", "brazil": "BR", "mexico": "MX", "argentina": "AR",
}

AGE_GROUP_MAP = {
    "child": "child",
    "children": "child",
    "kid": "child",
    "kids": "child",
    "teen": "teen",
    "teenager": "teen",
    "teens": "teen",
    "adult": "adult",
    "adults": "adult",
    "elderly": "elderly",
    "senior": "elderly",
    "seniors": "elderly",
    "old": "elderly",
}

GENDER_MAP = {
    "male": "male",
    "males": "male",
    "man": "male",
    "men": "male",
    "boy": "male",
    "boys": "male",
    "female": "female",
    "females": "female",
    "woman": "female",
    "women": "female",
    "girl": "female",
    "girls": "female",
    "lady": "female",
    "ladies": "female",
}


def parse_natural_language_query(query: str) -> Optional[Dict]:
    """
    This function parses plain English query into filter paramerters for searching the database.
    """

    if not query or not query.strip():
        return None
    
    query_lower = query.lower().strip()
    filters = {}

    for gender_word, gender_value in GENDER_MAP.items():
        if gender_word in query_lower:
            filters["gender"] = gender_value
            break
    
    for age_word, age_value in AGE_GROUP_MAP.items():
        if age_word in query_lower:
            filters["age_group"] = age_value
            break

    for country_name, country_code in COUNTRY_MAP.items():
        if country_name in query_lower:
            filters["country_id"] = country_code


    if "young" in query_lower:
        filters["min_age"] = 16
        filters["max_age"] = 24


    if "old" in query_lower and "above" not in query_lower and "over" not in query_lower:
        filters["min_age"] =60

    above_match = re.search(r'(?:above|over)\s+(\d+)', query_lower)
    if above_match:
        age = int(above_match.group(1))
        filters["min_age"] = age

    below_match = re.search(r'(?:below|under)\s+(\d+)', query_lower)
    if below_match:
        age = int(below_match.group(1))
        filters["max_age"] = age

    age_match = re.search(r'(?:age|aged)\s+(\d+)', query_lower)
    if age_match:
        age = int(age_match.group(1))
        filters["min_age"] = age
        filters["max_age"] = age


    if not filters:
        return None
    
    return filters


def validate_filter_params(
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    country_id: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    min_gender_probability: Optional[float] = None,
    min_country_probability: Optional[float] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    
    valid_age_groups = ["child", "teenager", "adult", "senior"]
    valid_sort_by = ["age", "created_at", "gender_probability"]
    valid_order = ["asc", "desc"]
    
    if gender and gender.lower() not in ["male", "female"]:
        return False, "Invalid gender value"
    
    if age_group and age_group.lower() not in valid_age_groups:
        return False, f"Invalid age_group. Must be one of: {', '.join(valid_age_groups)}"
    
    if min_age is not None and (min_age < 0 or min_age > 150):
        return False, "min_age must be between 0 and 150"
    
    if max_age is not None and (max_age < 0 or max_age > 150):
        return False, "max_age must be between 0 and 150"
    
    if min_age is not None and max_age is not None and min_age > max_age:
        return False, "min_age cannot be greater than max_age"
    
    if min_gender_probability is not None and (min_gender_probability < 0 or min_gender_probability > 1):
        return False, "min_gender_probability must be between 0 and 1"
    
    if min_country_probability is not None and (min_country_probability < 0 or min_country_probability > 1):
        return False, "min_country_probability must be between 0 and 1"
    
    if sort_by and sort_by.lower() not in valid_sort_by:
        return False, f"Invalid sort_by. Must be one of: {', '.join(valid_sort_by)}"
    
    if order and order.lower() not in valid_order:
        return False, f"Invalid order. Must be one of: {', '.join(valid_order)}"
    
    return True, None