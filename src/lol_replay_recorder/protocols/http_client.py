"""
Protocol definitions for HTTP client implementations.

This module provides protocol interfaces to standardize HTTP client behavior
across the application, enabling better testability and dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class HttpClient(ABC):
    """
    Protocol defining the interface for HTTP client implementations.

    This protocol standardizes HTTP client behavior across the application,
    supporting both synchronous and asynchronous operations with retry logic.
    """

    @abstractmethod
    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Target URL
            headers: HTTP headers
            json: JSON payload for request body
            data: Raw string data for request body
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing response data and metadata

        Raises:
            HttpClientError: When the request fails
        """
        pass

    @abstractmethod
    def retry_request(
        self,
        method: str,
        url: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry logic.

        Args:
            method: HTTP method
            url: Target URL
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Additional arguments passed to request()

        Returns:
            Dictionary containing response data and metadata

        Raises:
            HttpClientError: When all retries fail
        """
        pass


class HttpClientError(Exception):
    """Base exception for HTTP client errors."""
    pass