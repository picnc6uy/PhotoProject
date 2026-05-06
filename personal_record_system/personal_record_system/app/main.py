from fastapi import FastAPI

from .db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Record System API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
