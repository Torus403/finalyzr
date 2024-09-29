from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.api.main import api_router
from app.core.config import settings
from app.core.log_config import logging_settings

# This needs to be called before middleware is imported to ensure setup
logging_settings.setup()

from app.core.middleware import log_requests, add_request_id


limiter = Limiter(key_func=get_remote_address)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Welcome to Finalyzr's API documentation! Here you will be able to discover all the ways you can "
    "interact with the Finalyzr API.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.state.limiter = limiter


app.middleware("http")(log_requests)
app.middleware("http")(add_request_id)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


@app.get("/")
@limiter.limit("50/minute")
async def root(request: Request):
    return "Hello, World!"


app.include_router(api_router, prefix=settings.API_V1_STR)
