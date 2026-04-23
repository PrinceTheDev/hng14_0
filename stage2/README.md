# Intelligence Query Engine System - Stage 2

A FastAPI application for demographic intelligence with advanced **filtering**, **sorting**, **pagination**, and **natural language query parsing**.

---

## 📋 Database Schema

| Field | Type | Purpose |
|-------|------|---------|
| **id** | UUID v7 | Unique identifier (primary key) |
| **name** | VARCHAR + UNIQUE | Person's full name |
| **gender** | VARCHAR | "male" or "female" |
| **gender_probability** | FLOAT (0-1) | Confidence score from Genderize API |
| **age** | INT | Exact age in years |
| **age_group** | VARCHAR | child \| teenager \| adult \| senior |
| **country_id** | VARCHAR(2) | ISO 2-letter country code (NG, GH, KE) |
| **country_name** | VARCHAR | Full country name (Nigeria, Ghana, Kenya) |
| **country_probability** | FLOAT (0-1) | Confidence score from Nationalize API |
| **created_at** | TIMESTAMP | Auto-generated UTC timestamp |

---

## Setup & Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment (optional)
export DATABASE_URL="sqlite:////tmp/profile.db"

# 3. Seed database with 2026 profiles
python -m stage2.seed

# 4. Run the server
uvicorn stage2.main:app --reload


Server runs at: http://localhost:8000
Auto-generated docs: http://localhost:8000/docs


API Endpoints

1. GET /api/profiles — Advanced Filtering & Pagination
Returns all profiles with support for filtering, sorting, and pagination.

Query Parameters

Parameter	Type	Default	Notes
gender	string	None	"male" or "female"
age_group	string	None	"child", "teenager", "adult", or "senior"
country_id	string	None	ISO 2-letter code (e.g., "NG", "GH", "KE")
min_age	integer	None	Minimum age (0-150)
max_age	integer	None	Maximum age (0-150)
min_gender_probability	float	None	Minimum confidence (0-1)
min_country_probability	float	None	Minimum confidence (0-1)
sort_by	string	"created_at"	"age", "created_at", or "gender_probability"
order	string	"asc"	"asc" or "desc"
page	integer	1	Page number (1-indexed)
limit	integer	10	Results per page (1-50, max 50)


2. GET /api/profiles/search — Natural Language Query
Parse plain English queries and convert them to filters automatically (no SQL needed by user).

Query Parameters
Parameter	Type	Required	Notes
q	string	Yes	Natural language query (min 1 character)
page	integer	No	Page number (default: 1)
limit	integer	No	Results per page (default: 10, max: 50)



## Natural Language Query Parsing
How It Works
The parser uses rule-based keyword matching (no AI, no machine learning) to extract filter information from plain English queries.

Algorithm:

Convert query to lowercase
Search for keywords in this order: gender → age_group → country → age ranges
Extract first match for each category
Return filters dictionary

Input:  "young females from kenya"
Step 1: lowercase → "young females from kenya"
Step 2: scan for gender → find "females" → gender = "female"
Step 3: scan for age_group → (none found)
Step 4: scan for country → find "kenya" → country_id = "KE"
Step 5: scan for ages → find "young" → min_age = 16, max_age = 24
Output: {"gender": "female", "country_id": "KE", "min_age": 16, "max_age": 24}


## Supported Keywords
Gender Keywords

MALE:
  - male, males
  - man, men
  - boy, boys
  
FEMALE:
  - female, females
  - woman, women
  - girl, girls
  - lady, ladies

  CHILD (0-12):
  - child, children
  - kid, kids

TEENAGER (13-19):
  - teenager, teenagers
  - teen, teens
  - adolescent

ADULT (20-59):
  - adult, adults

SENIOR (60+):
  - senior, seniors
  - elderly
  - old


  # "above 30" or "over 25"
r'(?:above|over)\s+(\d+)'

# "below 25" or "under 30"
r'(?:below|under)\s+(\d+)'

# "age 35" or "aged 42"
r'(?:age|aged)\s+(\d+)'


## Limitations & What We DON'T Handle
1. Boolean Logic
Query:    "males OR females"
Parses as: {gender: "male"}  ← Only first match
Workaround: Use /api/profiles endpoint with explicit filters


2. Negation
Query:    "not males"
Parses as: Nothing (returns error)
Workaround: Use /api/profiles endpoint

3. Range Connectors
Query: "males 25 to 35"
Parses as: Nothing (returns error)

4. Multiple Countries
Parses as: {country_id: "NG"} --> Only first match
workaround: Query each country seperately


5. Probability Thresholds
Query:    "high confidence males"
Parses as: {gender: "male"}  ← Probability filters ignored
Workaround: Use /api/profiles?min_gender_probability=0.9

6. Typos & Spelling Variations
Query:    "nigera"  (misspelled)
Parses as: Nothing (returns error)
Workaround: Use correct spelling "nigeria" or use API filters\

7. Ambiguos Terms
Query:    "young"  without context
Parses as: {min_age: 16, max_age: 24}  ← Hard-coded range
Workaround: Use /api/profiles?min_age=X&max_age=Y for custom ranges

8. Multiple Age Specifications
Query:    "ages 20 to 30 above 25"
Parses as: {min_age: 20, max_age: 30}  ← First match wins
Workaround: Use single age specification in query

9. Context Awareness
Query:    "old children"
Parses as: {age_group: "child", min_age: 60}  ← Contradictory!
Workaround: Be specific in queries, don't mix contradictory terms


10. Complex Description
Query:    "I'm looking for young, single, educated males from Nigeria"
Parses as: {gender: "male", country_id: "NG", min_age: 16, max_age: 24}
Note:     Only standard keywords extracted; "single", "educated" ignored
Workaround: Stick to supported keywords