"""Base HTTP client with common retry logic and error handling.

This module provides the BaseHTTPClient class that encapsulates common HTTP functionality
including retry logic, SSL verification settings, and standardized error handling.
"""

from __future__ import annotations

import asyncio
import httpx
from typing import Any, Dict, Optional

from ...domain.errors import HTTPError


class BaseHTTPClient:
    """Base HTTP client with common functionality for Riot API clients.

    Provides:
    - Configurable SSL verification
    - Common retry logic with exponential backoff
    - Standardized error handling with HTTPError
    - JSON response parsing with fallback
    """

    def __init__(self, verify_ssl: bool = False, timeout: float = 30.0):
        """Initialize the HTTP client.

        Args:
            verify_ssl: Whether to verify SSL certificates (default: False for Riot's self-signed certs)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.verify_ssl = verify_ssl
        self.timeout = timeout

    async def request_with_retry(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        retries: int = 5,
        base_delay: float = 0.1,
    ) -> Any:
        """Make HTTP request with retry logic and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            headers: Optional request headers
            body: Optional request body (JSON)
            retries: Number of retry attempts (default: 5)
            base_delay: Base delay for exponential backoff (default: 0.1s)

        Returns:
            Parsed JSON response or raw response object

        Raises:
            HTTPError: When request fails after all retries
        """
        if retries < 0:
            raise HTTPError(url, 0, "Max retries exceeded")

        # Prepare headers with Content-Type for non-GET requests
        request_headers = {}
        if headers:
            request_headers.update(headers)

        if method.upper() != "GET":
            request_headers["Content-Type"] = "application/json"

        try:
            async with httpx.AsyncClient(
                verify=self.verify_ssl,
                timeout=self.timeout
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    json=body if method.upper() != "GET" else None,
                )

                if not response.is_success:
                    # For 404 errors, don't retry - raise immediately
                    if response.status_code == 404:
                        raise HTTPError(
                            url,
                            response.status_code,
                            "Failed to find the requested resource."
                        )

                    # For other errors, retry if attempts remain
                    if retries <= 0:
                        raise HTTPError(
                            url,
                            response.status_code,
                            f"HTTP {response.status_code} {response.reason_phrase}"
                        )

                    # Wait before retry
                    await asyncio.sleep(base_delay * (6 - retries))  # Exponential backoff
                    return await self.request_with_retry(
                        method, url, headers, body, retries - 1, base_delay
                    )

                # Try to parse JSON response
                try:
                    return response.json()
                except Exception:
                    # Return raw response if JSON parsing fails
                    return response

        except httpx.RequestError as e:
            # Handle connection errors, timeouts, etc.
            if retries <= 0:
                raise HTTPError(url, 0, str(e))

            # Wait before retry
            await asyncio.sleep(base_delay * (6 - retries))
            return await self.request_with_retry(
                method, url, headers, body, retries - 1, base_delay
            )

        except HTTPError:
            # Re-raise HTTP errors without modification
            raise
        except Exception as e:
            # Handle any other unexpected errors
            if retries <= 0:
                raise HTTPError(url, 0, f"Unexpected error: {str(e)}")

            # Wait before retry
            await asyncio.sleep(base_delay * (6 - retries))
            return await self.request_with_retry(
                method, url, headers, body, retries - 1, base_delay
            )