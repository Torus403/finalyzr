from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings
from app.core.log_config import logging_settings

# This needs to be called before middleware is imported to ensure setup
logging_settings.setup()

from app.core.middleware import log_requests, add_request_id

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Welcome to Finalyzr's API documentation! Here you will be able to discover all the ways you can "
    "interact with the Finalyzr API.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.middleware("http")(log_requests)
app.middleware("http")(add_request_id)


@app.get("/")
async def root():
    return "Hello, World!"


app.include_router(api_router, prefix=settings.API_V1_STR)
