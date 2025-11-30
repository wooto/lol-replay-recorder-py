"""Enhanced error classes for lol-replay-recorder domain.

This module provides a hierarchy of custom error classes for better error handling
and debugging throughout the application.
"""

from __future__ import annotations


class CustomError(Exception):
    """Base error for lol-replay-recorder.

    All custom exceptions in the application should inherit from this class
    to maintain consistent error handling and logging.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        if self.args:
            return str(self.args[0])
        return ""


class HTTPError(CustomError):
    """HTTP request failed with detailed context.

    Attributes:
        url: The URL that was being accessed
        status_code: HTTP status code (0 for connection errors)
        message: Detailed error message
    """

    def __init__(self, url: str, status_code: int, message: str) -> None:
        self.url = url
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code} for {url}: {message}")

    def __repr__(self) -> str:
        return f"HTTPError(url={self.url!r}, status_code={self.status_code}, message={self.message!r})"


class LockfileError(CustomError):
    """Lockfile not found or invalid.

    Raised when the League Client lockfile cannot be found, read, or parsed.
    This typically indicates that the League Client is not running or has crashed.
    """

    def __init__(self, message: str = "Lockfile not found or invalid") -> None:
        super().__init__(message)


class ProcessError(CustomError):
    """Process management failed.

    Raised when operations on system processes fail, such as:
    - Starting/stopping League Client processes
    - Process not found or already terminated
    - Insufficient permissions for process operations
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConfigError(CustomError):
    """Configuration error.

    Raised when configuration files cannot be:
    - Found or accessed
    - Parsed (invalid INI/YAML syntax)
    - Updated or saved due to permission issues
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)