from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import AppException, ErrorCode
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


def _error_code_from_status_code(status_code: int) -> str:
    if status_code == 401:
        return ErrorCode.UNAUTHORIZED.value
    if status_code == 403:
        return ErrorCode.FORBIDDEN.value
    if status_code == 404:
        return ErrorCode.NOT_FOUND.value
    if status_code == 409:
        return ErrorCode.CONFLICT.value
    if status_code == 422:
        return ErrorCode.VALIDATION_ERROR.value
    if status_code >= 500:
        return ErrorCode.INTERNAL_ERROR.value
    return ErrorCode.VALIDATION_ERROR.value


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code.value,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"][1:]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Validation error",
                "details": details,
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": _error_code_from_status_code(exc.status_code),
                "message": str(exc.detail),
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    del exc
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "Internal server error",
            }
        },
    )


@app.get(f"{settings.api_v1_str}/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    """Simple root status endpoint."""
    return {"message": "Rubika Bot SaaS API"}
