"""
Domain layer package for lol-replay-recorder.

This package contains the core domain entities, types, and error definitions
that form the foundation of the application's business logic.
"""

from . import entities, types
from .errors import (
    ConfigError,
    CustomError,
    HTTPError,
    LockfileError,
    ProcessError,
)

__all__ = [
    "entities",
    "types",
    "CustomError",
    "HTTPError",
    "LockfileError",
    "ProcessError",
    "ConfigError",
]