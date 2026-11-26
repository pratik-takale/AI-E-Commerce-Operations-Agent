# AI E-Commerce Operations Agent

An AI-powered e-commerce operations platform where specialized agents answer product questions, check inventory, track orders, and handle customer issues.

**Tech stack:** React, FastAPI, PostgreSQL, Redis, LangChain/LangGraph

## Documentation
- [Project Requirements](docs/PROJECT_REQUIREMENTS.md)
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [API Design](docs/API_DESIGN.md)
- [Database Design](docs/DATABASE_DESIGN.md)

## Status
Day 1: Requirement analysis and system design (in progress)
## Run the backend locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env      # then edit DATABASE_URL
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

- Health check: http://127.0.0.1:8000/health
- Swagger docs: http://127.0.0.1:8000/docs