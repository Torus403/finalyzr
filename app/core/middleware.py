import contextvars
import logging
import time
import uuid

from fastapi import Request

from app.core.log_config import logging_settings

request_id_var = contextvars.ContextVar("request_id", default=None)

logger = logging.getLogger(logging_settings.LOGGER_NAME)


async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(f"Incoming request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(
            f"Unhandled exception for request {request.method} {request.url.path}: {e}"
        )
        raise e

    process_time = time.perf_counter() - start_time
    logger.info(
        f"Completed request: {request.method} {request.url.path} "
        f"Status: {response.status_code} Duration: {process_time:.2f}s"
    )
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    # logger.info(f"Request ID {request_id} completed.")
    return response


def some_function():
    request_id = request_id_var.get()
    logger.info(f"Processing with request ID: {request_id}")
