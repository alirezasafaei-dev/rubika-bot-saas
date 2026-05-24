from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.api.v1.endpoints.webhooks import (
    _normalize_rubika_payload,
    _validate_channel_id,
    _validate_event_type,
    get_webhook_service,
)
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import AppException, ErrorCode
from app.core.logging import setup_logging
from app.db.session import engine
from app.schemas.webhook import RubikaWebhookAdapterPayload, RubikaWebhookResponse
from app.services.webhook_service import WebhookService
from app.workers.queue import redis_ping

STATIC_DIR = Path(__file__).resolve().parent / "static"

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


async def _database_ready() -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@app.get(f"{settings.api_v1_str}/ready")
async def readiness_check() -> JSONResponse:
    """Readiness endpoint for deployment verification."""
    database_ready = await _database_ready()

    try:
        queue_ready = redis_ping()
    except Exception:
        queue_ready = False

    services = {
        "database": "ok" if database_ready else "error",
        "redis": "ok" if queue_ready else "error",
    }
    is_ready = all(status == "ok" for status in services.values())
    status_code = 200 if is_ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if is_ready else "degraded",
            "services": services,
        },
    )


@app.get("/admin", response_class=FileResponse)
async def admin_panel() -> FileResponse:
    return FileResponse(STATIC_DIR / "admin.html")


@app.get("/")
async def root() -> dict[str, str]:
    """Simple root status endpoint."""
    return {"message": "Rubika Bot SaaS API"}


@app.post("/", response_model=RubikaWebhookResponse)
async def root_webhook(
    payload: RubikaWebhookAdapterPayload,
    service: Annotated[WebhookService, Depends(get_webhook_service)],
) -> RubikaWebhookResponse:
    normalized = _normalize_rubika_payload(payload.model_dump())
    event_type = _validate_event_type(normalized.get("event_type"))
    rubika_channel_id = _validate_channel_id(normalized.get("rubika_channel_id"))
    payload_data = {
        "event_type": event_type,
        "message": normalized.get("message"),
        "sender_rubika_user_id": normalized.get("sender_rubika_user_id"),
        "message_id": normalized.get("message_id"),
    }

    if event_type == "message_received":
        result = await service.process_message_event_from_rubika_channel(
            rubika_channel_id=rubika_channel_id,
            secret=None,
            payload=payload_data,
        )
    else:
        result = await service.process_delivery_event_from_rubika_channel(
            rubika_channel_id=rubika_channel_id,
            secret=None,
            payload=payload_data,
        )

    return RubikaWebhookResponse(
        accepted=bool(result["accepted"]),
        reason=result.get("reason") or f"accepted:{event_type}",
    )
