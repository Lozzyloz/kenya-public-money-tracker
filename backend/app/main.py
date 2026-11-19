from fastapi import FastAPI

from app.api import counties, finance, health, projects

app = FastAPI(title="Kenya Public Money Tracker API", version="0.1.0")
app.include_router(health.router, prefix="/api/v1")
app.include_router(counties.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(finance.router, prefix="/api/v1")
