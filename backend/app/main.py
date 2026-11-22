from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    audit, auth, counties, documents, finance, health,
    progress, projects, reference, sectors, users,
)
from app.core.config import settings

app = FastAPI(title="Kenya Public Money Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (
    health, auth, users, counties, sectors, reference,
    documents, projects, finance, progress, audit,
):
    app.include_router(module.router, prefix="/api/v1")
