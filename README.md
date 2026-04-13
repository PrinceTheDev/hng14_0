# GENDER CLASSIFICATION API

A simple, fast, production ready API that classifies a given name by gender using the Genderize API, processes the response and returns a structured result.

## OVERVIEW

This API accepts a name as a query parameter, fetches gender prediction data from an external service, applies validation and business logic, and returns a clean, standardized response.

It is built using FastAPI with asynchronous request handling for high performance.

## FEATURES

* Input validation for query parameters
* External API integration (Genderize)
* Data transformation and formatting
* Confidence scoring logic
* Proper error handling with HTTP status code
* CORS enabled for cross-origin requests
* Health check endpoint
* Asynchronous and scalable design

## TECH STACK

* Python
* FAST API
* HTTPX


## PROJECT STRUCTURE

├── main.py
├── requirements.txt
└── README.md


## Installation & Setup

1. Clone the repository
* git clone https://github.com/your-username/gender-classification-api.git
* cd gender-classification-api
2. Create a virtual environment
* python -m venv venv
* source venv/bin/activate   # Windows: venv\Scripts\activate
3. Install dependencies
* pip install -r requirements.txt


## Running the Server
uvicorn main:app --reload

Server will start at:

* http://127.0.0.1:8000


## API Endpoints

1. Classify Name

* GET /api/classify?name={name}

Example Request
/api/classify?name=john
Success Response (200)
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 1234,
    "is_confident": true,
    "processed_at": "2026-04-01T12:00:00Z"
  }
}


## Processing Logic
* count → renamed to sample_size
* is_confident is true when:
* probability >= 0.7
* AND sample_size >= 100
* processed_at is generated dynamically in UTC (ISO 8601)


## Error Handling

All errors follow this format:

{
  "status": "error",
  "message": "Error message here"
}