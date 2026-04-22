# Intelligence Query Engine System - Stage 2

A FastAPI application for demographic intelligence with advanced filtering, sorting, pagination, and **natural language query parsing**.

## Database Schema

| Field | Type | Notes |
|-------|------|-------|
| id | UUID v7 | Primary key |
| name | VARCHAR + UNIQUE | Person's full name |
| gender | VARCHAR | "male" or "female" |
| gender_probability | FLOAT | Confidence score (0-1) |
| age | INT | Exact age |
| age_group | VARCHAR | child, teenager, adult, senior |
| country_id | VARCHAR(2) | ISO code (NG, BJ, KE, etc.) |
| country_name | VARCHAR | Full country name |
| country_probability | FLOAT | Confidence score (0-1) |
| created_at | TIMESTAMP | Auto-generated UTC |

## Setup & Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set database URL (optional)
export DATABASE_URL="sqlite:////tmp/profile.db"

# Seed database with 2026 profiles
python -m stage2.seed

# Run the server
uvicorn stage2.main:app --reload