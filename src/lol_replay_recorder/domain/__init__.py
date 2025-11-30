"""Domain package for lol-replay-recorder.

This package contains pure domain types, entities, and errors that form the
core of the application's business logic.
"""

from .errors import ConfigError, CustomError, HTTPError, LockfileError, ProcessError

__all__ = ["CustomError", "HTTPError", "LockfileError", "ProcessError", "ConfigError"]