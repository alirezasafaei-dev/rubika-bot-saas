# app/core/errors.py
from enum import Enum


class ErrorCode(str, Enum):
    # General
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    FORBIDDEN = "FORBIDDEN"
    UNAUTHORIZED = "UNAUTHORIZED"

    # Auth
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"

    # Workspace
    WORKSPACE_NOT_FOUND = "WORKSPACE_NOT_FOUND"
    WORKSPACE_ALREADY_EXISTS = "WORKSPACE_ALREADY_EXISTS"

    # Workspace Member
    NOT_WORKSPACE_MEMBER = "NOT_WORKSPACE_MEMBER"
    NOT_WORKSPACE_ADMIN = "NOT_WORKSPACE_ADMIN"

    # Channel
    CHANNEL_NOT_FOUND = "CHANNEL_NOT_FOUND"
    CHANNEL_ALREADY_EXISTS = "CHANNEL_ALREADY_EXISTS"

    # Scheduled Post
    SCHEDULED_POST_NOT_FOUND = "SCHEDULED_POST_NOT_FOUND"
    SCHEDULED_POST_INVALID_TIME = "SCHEDULED_POST_INVALID_TIME"

    # Auto Reply
    AUTO_REPLY_NOT_FOUND = "AUTO_REPLY_NOT_FOUND"
    AUTO_REPLY_ALREADY_EXISTS = "AUTO_REPLY_ALREADY_EXISTS"

    # Filter
    FILTER_NOT_FOUND = "FILTER_NOT_FOUND"
    FILTER_ALREADY_EXISTS = "FILTER_ALREADY_EXISTS"

    # Webhook
    WEBHOOK_NOT_FOUND = "WEBHOOK_NOT_FOUND"
    WEBHOOK_ALREADY_EXISTS = "WEBHOOK_ALREADY_EXISTS"


class AppException(Exception):
    def __init__(self, error_code: ErrorCode, message: str | None = None, status_code: int = 400):
        self.error_code = error_code
        self.message = message or error_code.value.replace("_", " ").title()
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    def __init__(self, error_code: ErrorCode, message: str | None = None):
        super().__init__(error_code, message, status_code=404)


class ConflictError(AppException):
    def __init__(self, error_code: ErrorCode, message: str | None = None):
        super().__init__(error_code, message, status_code=409)


class PermissionDeniedError(AppException):
    def __init__(self, error_code: ErrorCode, message: str | None = None):
        super().__init__(error_code, message, status_code=403)


class UnauthorizedError(AppException):
    def __init__(self, error_code: ErrorCode, message: str | None = None):
        super().__init__(error_code, message, status_code=401)
