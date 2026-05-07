# app/core/errors.py
from enum import StrEnum
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


class ErrorCode(StrEnum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_TOKEN = "INVALID_TOKEN"
    INVALID_REFRESH_TOKEN = "INVALID_REFRESH_TOKEN"
    REFRESH_TOKEN_EXPIRED = "REFRESH_TOKEN_EXPIRED"
    REFRESH_TOKEN_REVOKED = "REFRESH_TOKEN_REVOKED"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    WORKSPACE_NOT_FOUND = "WORKSPACE_NOT_FOUND"
    WORKSPACE_ACCESS_DENIED = "WORKSPACE_ACCESS_DENIED"

    CHANNEL_NOT_FOUND = "CHANNEL_NOT_FOUND"
    CHANNEL_ACCESS_DENIED = "CHANNEL_ACCESS_DENIED"

    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"

    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"


ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INVALID_CREDENTIALS: "Invalid email or password",
    ErrorCode.EMAIL_ALREADY_EXISTS: "Email already registered",
    ErrorCode.INVALID_TOKEN: "Invalid or expired token",
    ErrorCode.INVALID_REFRESH_TOKEN: "Invalid refresh token",
    ErrorCode.REFRESH_TOKEN_EXPIRED: "Refresh token expired",
    ErrorCode.REFRESH_TOKEN_REVOKED: "Refresh token has been revoked",
    ErrorCode.USER_NOT_FOUND: "User not found",
    ErrorCode.UNAUTHORIZED: "Authentication required",
    ErrorCode.FORBIDDEN: "Access forbidden",
    ErrorCode.WORKSPACE_NOT_FOUND: "Workspace not found",
    ErrorCode.WORKSPACE_ACCESS_DENIED: "Access to workspace denied",
    ErrorCode.CHANNEL_NOT_FOUND: "Channel not found",
    ErrorCode.CHANNEL_ACCESS_DENIED: "Access to channel denied",
    ErrorCode.VALIDATION_ERROR: "Validation error",
    ErrorCode.INVALID_INPUT: "Invalid input data",
    ErrorCode.INTERNAL_ERROR: "Internal server error",
    ErrorCode.DATABASE_ERROR: "Database operation failed",
}

ERROR_STATUS_CODES: dict[ErrorCode, int] = {
    ErrorCode.INVALID_CREDENTIALS: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.EMAIL_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    ErrorCode.INVALID_TOKEN: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.INVALID_REFRESH_TOKEN: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.REFRESH_TOKEN_EXPIRED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.REFRESH_TOKEN_REVOKED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ErrorCode.WORKSPACE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.WORKSPACE_ACCESS_DENIED: status.HTTP_403_FORBIDDEN,
    ErrorCode.CHANNEL_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.CHANNEL_ACCESS_DENIED: status.HTTP_403_FORBIDDEN,
    ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ErrorCode.INVALID_INPUT: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ErrorCode.INTERNAL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


class AppException(Exception):
    def __init__(
        self,
        error_code: ErrorCode,
        detail: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        self.error_code = error_code
        self.detail = detail or ERROR_MESSAGES[error_code]
        self.meta = meta or {}
        super().__init__(self.detail)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    return JSONResponse(
        status_code=ERROR_STATUS_CODES.get(
            exc.error_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ),
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "meta": exc.meta,
            }
        },
    )
