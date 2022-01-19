import time
from typing import List

from loguru import logger
from starlette.middleware import Middleware
from starlette_context import context, plugins
from starlette_context.middleware import ContextMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log specific info.
    """
    async def dispatch(self, request: Request, call_next):
        x_requests_id = context.data["X-Request-ID"]
        logger.info(f" {x_requests_id} | {request.url.path} ")
        logger.info(f" {x_requests_id} | {request.headers} ")
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time)
        formatted_process_time = f'{process_time:0.4f}'
        response.headers["X-Processes-Time"] = formatted_process_time
        logger.info(f" {x_requests_id} | finished after {formatted_process_time}")
        return response


def configure_middleware() -> List:
    """
    Creates a middleware instance using plugins and more extensive logging
    """
    middleware = [
        Middleware(
            ContextMiddleware,
            plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
        ),
        Middleware(LoggerMiddleware),
    ]
    return middleware
