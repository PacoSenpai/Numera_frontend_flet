# core/exceptions.py
"""Custom exceptions for the application"""

class APIError(Exception):
    """Base exception for API-related errors"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    pass

class NetworkError(APIError):
    """Raised when network connectivity issues occur"""
    pass

class ValidationError(APIError):
    """Raised when data validation fails"""
    pass

class NotFoundError(APIError):
    """Raised when requested resource is not found"""
    pass

class ServerError(APIError):
    """Raised when server returns 5xx errors"""
    pass