from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, counties, finance, health, projects, users
from app.core.config import settings

app = FastAPI(title="Kenya Public Money Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (health, auth, users, counties, projects, finance):
    app.include_router(module.router, prefix="/api/v1")
