from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Welcome to Finalyzr's API documentation! Here you will be able to discover all the ways you can "
    "interact with the Finalyzr API.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.get("/")
async def root():
    return "Hello, World!"


app.include_router(api_router, prefix=settings.API_V1_STR)
