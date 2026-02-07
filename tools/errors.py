from __future__ import annotations


class ToolError(Exception):
    """Base error for predictable tool failures (bad input, network issues, etc.)."""


class ValidationError(ToolError):
    """Raised when params are invalid for a tool."""


class NetworkError(ToolError):
    """Raised for network/HTTP related failures."""
