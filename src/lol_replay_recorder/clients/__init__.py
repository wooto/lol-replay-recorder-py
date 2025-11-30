"""Client modules for external service communication.

This package provides HTTP clients and other client implementations
for communicating with external services like Riot APIs and window automation.
"""

# Import main HTTP clients for easy access
from .http.lcu import LCUClient
from .http.riot import RiotAPIClient
from .http.base import BaseHTTPClient

__all__ = [
    "LCUClient",
    "RiotAPIClient",
    "BaseHTTPClient",
]