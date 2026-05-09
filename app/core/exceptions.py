# app/core/exceptions.py
from .errors import (
    AppException,
    ConflictError,
    ErrorCode,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
)

# Aliases for backward compatibility
ConflictException = ConflictError
NotFoundException = NotFoundError
ForbiddenException = PermissionDeniedError
UnauthorizedException = UnauthorizedError


class UnprocessableEntity(AppException):
    def __init__(self, error_code: ErrorCode, message: str | None = None):
        super().__init__(error_code, message, status_code=422)


class InternalServerError(AppException):
    def __init__(self, error_code: ErrorCode, message: str | None = None):
        super().__init__(error_code, message, status_code=500)


__all__ = [
    "AppException",
    "ConflictError",
    "ConflictException",
    "ErrorCode",
    "ForbiddenException",
    "InternalServerError",
    "NotFoundError",
    "NotFoundException",
    "PermissionDeniedError",
    "UnauthorizedException",
    "UnauthorizedError",
    "UnprocessableEntity",
]
