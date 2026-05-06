# Personal Record System

This project collects and normalises personal data (contacts, calendar events, messages, media) into a self-owned "pod" that can power future dashboards and automation.

## Goals
- Provide a portable, container-friendly stack.
- Ingest data from Google services into a SQLite-backed store (Postgres-ready).
- Normalise entities (people, events, messages, media) with change tracking.
- Expose a FastAPI service (`/health`, `/people`, etc.) for agent/dashboards to consume.

## Getting Started (MVP)
1. Create a `.env` file based on `.env.example` with Google API credentials.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the API locally: `uvicorn personal_record_system.app.main:app --reload`.
4. (Future) run ingestion scripts to populate the pod.

Docker support is provided via `docker-compose.yml` for a consistent runtime across environments.
