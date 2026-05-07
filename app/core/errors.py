# app/core/errors.py

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, Response


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def app_exception_handler(request: Request, exc: Exception) -> Response:
    """Global handler for AppException."""
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    """Global handler for HTTPException."""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> Response:
    """Catch-all handler for unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
