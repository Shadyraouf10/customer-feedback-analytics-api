# Customer Feedback Analytics API

A portfolio-ready backend project built with Python and FastAPI. It collects,
stores, filters, updates, and summarizes customer feedback through documented
REST endpoints.

## Why this project

The project demonstrates backend fundamentals that are useful in data-driven
products: API design, validation, relational persistence, filtering, analytics,
testing, and clear documentation.

## Current features

- Create, read, update, and delete customer feedback
- Automatic rule-based sentiment label: positive, negative, or neutral
- Filter by sentiment and source, with pagination
- Analytics endpoint with counts and percentages
- SQLite persistence through SQLAlchemy 2.0
- Request validation with Pydantic
- Interactive OpenAPI/Swagger documentation
- Automated API tests with pytest

> The sentiment component is intentionally a transparent rule-based MVP. A
> future version can replace it with a trained or pre-trained NLP model.

## Project structure

```text
app/
  database.py   Database configuration and session dependency
  main.py       FastAPI application and endpoints
  models.py     SQLAlchemy database models
  schemas.py    Request and response validation models
  sentiment.py  MVP sentiment analysis logic
tests/
  test_api.py   API lifecycle and validation tests
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

## Example request

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Sara Ahmed","text":"The service was excellent and fast","source":"mobile-app"}'
```

## Run tests

```bash
pytest -q
```

## Planned improvements

- JWT authentication and user roles
- PostgreSQL support and migrations
- NLP-based sentiment model
- Docker setup and deployment
- More analytics filters and test coverage

