"""
Custom exceptions for the application.
"""
from typing import Optional, Any, Dict


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", resource: str = "resource"):
        super().__init__(
            message=f"{resource} not found: {message}",
            status_code=404,
            error_code="NOT_FOUND"
        )


class UnauthorizedException(AppException):
    """Authentication required or invalid."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )


class ForbiddenException(AppException):
    """Access denied."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )


class BadRequestException(AppException):
    """Invalid request."""

    def __init__(self, message: str = "Invalid request", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details
        )


class ConflictException(AppException):
    """Resource conflict."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT"
        )


class ValidationException(AppException):
    """Validation error."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


def format_error_response(exc: AppException) -> Dict[str, Any]:
    """Format an exception as an error response."""
    return {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    }