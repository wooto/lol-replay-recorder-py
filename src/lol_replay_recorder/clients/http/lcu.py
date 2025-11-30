"""League Client Update (LCU) API client.

This module provides the LCUClient class for making authenticated requests
to the League Client Update API using lockfile credentials.
"""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Any, Dict, Optional

from .base import BaseHTTPClient
from .constants import (
    VERIFY_SSL_DEFAULT,
    LOCKFILE_PARTS_COUNT,
    LOCKFILE_PROCESS_INDEX,
    LOCKFILE_PID_INDEX,
    LOCKFILE_PORT_INDEX,
    LOCKFILE_PASSWORD_INDEX,
    LOCKFILE_PROTOCOL_INDEX,
    RIOT_AUTH_USERNAME,
    LCU_BASE_URL_PATTERN,
    AUTHORIZATION_HEADER,
    BASIC_AUTH_PREFIX,
)
from ...constants import LOCKFILE_WAIT_TIMEOUT, DEFAULT_RETRY_COUNT
from ...domain.errors import HTTPError, LockfileError


class LCUClient(BaseHTTPClient):
    """Client for League Client Update (LCU) API.

    Handles authentication via lockfile and provides methods for common LCU endpoints.
    The LCU API uses self-signed certificates and requires basic authentication
    with credentials extracted from the League Client lockfile.
    """

    def __init__(self, lockfile_path: Optional[str] = None, **kwargs: Any):
        """Initialize LCU client.

        Args:
            lockfile_path: Path to League Client lockfile (if None, must be provided later)
            **kwargs: Additional arguments passed to BaseHTTPClient
        """
        super().__init__(verify_ssl=VERIFY_SSL_DEFAULT, **kwargs)  # LCU always uses self-signed certs
        self._lockfile_path = lockfile_path
        self._cached_credentials: Optional[Dict[str, str]] = None

    @property
    def lockfile_path(self) -> Optional[str]:
        """Get the current lockfile path."""
        return self._lockfile_path

    @lockfile_path.setter
    def lockfile_path(self, path: str) -> None:
        """Set the lockfile path and clear cached credentials."""
        self._lockfile_path = path
        self._cached_credentials = None

    async def _read_lockfile(self, lockfile_path: str) -> Dict[str, str]:
        """Read League Client lockfile and extract credentials.

        Args:
            lockfile_path: Path to the lockfile

        Returns:
            Dictionary containing 'port' and 'password' keys

        Raises:
            LockfileError: If lockfile not found or invalid
        """
        if self._cached_credentials and self._lockfile_path == lockfile_path:
            return self._cached_credentials

        # Wait for lockfile to exist
        path = Path(lockfile_path)
        timeout = LOCKFILE_WAIT_TIMEOUT  # seconds
        elapsed = 0

        while not path.exists() and elapsed < timeout:
            await asyncio.sleep(1)
            elapsed += 1

        if not path.exists():
            raise LockfileError(f"Lockfile not found: {lockfile_path}")

        try:
            content = path.read_text(encoding="utf-8")
            parts = content.split(":")

            if len(parts) < LOCKFILE_PARTS_COUNT:
                raise LockfileError(f"Invalid lockfile format: {lockfile_path}")

            credentials = {
                "port": parts[LOCKFILE_PORT_INDEX],
                "password": parts[LOCKFILE_PASSWORD_INDEX],
            }

            # Cache credentials if they match current lockfile path
            if self._lockfile_path == lockfile_path:
                self._cached_credentials = credentials

            return credentials

        except (OSError, IndexError) as e:
            raise LockfileError(f"Failed to parse lockfile {lockfile_path}: {str(e)}")

    def _create_auth_headers(self, password: str) -> Dict[str, str]:
        """Create basic authentication headers for LCU API.

        Args:
            password: Password from lockfile

        Returns:
            Dictionary containing Authorization header
        """
        auth_string = f"{RIOT_AUTH_USERNAME}:{password}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")

        return {
            AUTHORIZATION_HEADER: f"{BASIC_AUTH_PREFIX} {auth_b64}",
            "Content-Type": "application/json",
        }

    async def request(
        self,
        endpoint: str,
        method: str = "GET",
        body: Optional[Dict[str, Any]] = None,
        retries: int = DEFAULT_RETRY_COUNT,
        lockfile_path: Optional[str] = None,
    ) -> Any:
        """Make authenticated request to LCU API.

        Args:
            endpoint: API endpoint (e.g., '/lol-summoner/v1/current-summoner')
            method: HTTP method (default: GET)
            body: Optional request body (JSON)
            retries: Number of retry attempts (default: 3)
            lockfile_path: Override lockfile path for this request

        Returns:
            Parsed JSON response or raw response object

        Raises:
            LockfileError: If lockfile not found or invalid
            HTTPError: If request fails after retries
        """
        if not self._lockfile_path and not lockfile_path:
            raise LockfileError("No lockfile path configured")

        lockfile_path_to_use = lockfile_path or self._lockfile_path
        credentials = await self._read_lockfile(lockfile_path_to_use)  # type: ignore

        port = credentials["port"]
        password = credentials["password"]
        url = LCU_BASE_URL_PATTERN.format(host=RIOT_REPLAY_API_HOST, port=port) + endpoint
        headers = self._create_auth_headers(password)

        try:
            return await self.request_with_retry(
                method=method,
                url=url,
                headers=headers,
                body=body,
                retries=retries,
                base_delay=0.1,
            )
        except HTTPError as e:
            # Add LCU-specific context to error message
            raise HTTPError(
                e.url,
                e.status_code,
                f"LCU Request Error: {e.message}"
            ) from e

    # Common LCU API convenience methods
    async def get_current_summoner(self) -> Dict[str, Any]:
        """Get current summoner information.

        Returns:
            Dictionary containing summoner data
        """
        return await self.request("/lol-summoner/v1/current-summoner")

    async def get_lobby_data(self) -> Dict[str, Any]:
        """Get current lobby data.

        Returns:
            Dictionary containing lobby information
        """
        return await self.request("/lol-lobby/v2/lobby")

    async def create_lobby(self, lobby_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lobby.

        Args:
            lobby_data: Lobby configuration data

        Returns:
            Dictionary containing created lobby information
        """
        return await self.request(
            "/lol-lobby/v2/lobby",
            method="POST",
            body=lobby_data
        )

    async def get_gameflow_session(self) -> Dict[str, Any]:
        """Get current gameflow session.

        Returns:
            Dictionary containing gameflow session data
        """
        return await self.request("/lol-gameflow/v1/session")

    async def get_client_settings(self) -> Dict[str, Any]:
        """Get client settings.

        Returns:
            Dictionary containing client settings
        """
        return await self.request("/lol-settings/v1/game-settings")

    async def update_client_settings(
        self,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update client settings.

        Args:
            settings: Settings data to update

        Returns:
            Dictionary containing updated settings
        """
        return await self.request(
            "/lol-settings/v1/game-settings",
            method="PATCH",
            body=settings
        )