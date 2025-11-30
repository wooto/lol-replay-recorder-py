"""Riot Replay API client.

This module provides the RiotAPIClient class for making requests to the Riot Replay API.
The Riot Replay API uses self-signed certificates and runs on localhost:2999 when a replay is active.
"""

from __future__ import annotations

import httpx
from typing import Any, Dict, Optional

from .base import BaseHTTPClient
from .constants import (
    RIOT_REPLAY_API_HOST,
    RIOT_REPLAY_API_PORT,
    RIOT_REPLAY_BASE_URL,
    VERIFY_SSL_DEFAULT,
)
from ...constants import (
    DEFAULT_TIMEOUT,
    REPLAY_READY_RETRY_COUNT,
    REPLAY_READY_TIMEOUT,
    REPLAY_READY_CHECK_INTERVAL,
    RIOT_API_RETRY_COUNT,
)
from ...domain.errors import HTTPError


class RiotAPIClient(BaseHTTPClient):
    """Client for Riot Replay API.

    Handles requests to the Riot Replay API which controls replay playback,
    recording, and rendering properties. The API runs on localhost:2999
    when a replay is active and uses self-signed certificates.
    """

    def __init__(self, host: str = RIOT_REPLAY_API_HOST, port: int = RIOT_REPLAY_API_PORT, **kwargs: Any):
        """Initialize Riot API client.

        Args:
            host: API host (default: 127.0.0.1)
            port: API port (default: 2999)
            **kwargs: Additional arguments passed to BaseHTTPClient
        """
        super().__init__(verify_ssl=VERIFY_SSL_DEFAULT, **kwargs)  # Riot API always uses self-signed certs
        self.host = host
        self.port = port
        self.base_url = RIOT_REPLAY_BASE_URL

    async def request(
        self,
        endpoint: str,
        method: str = "GET",
        body: Optional[Dict[str, Any]] = None,
        retries: int = RIOT_API_RETRY_COUNT,
    ) -> Any:
        """Make request to Riot Replay API.

        Args:
            endpoint: API endpoint (e.g., '/replay/render')
            method: HTTP method (default: GET)
            body: Optional request body (JSON)
            retries: Number of retry attempts (default: 5)

        Returns:
            Parsed JSON response or raw response object

        Raises:
            HTTPError: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"

        try:
            return await self.request_with_retry(
                method=method,
                url=url,
                headers=None,  # Riot API doesn't require special headers
                body=body,
                retries=retries,
                base_delay=0.1,
            )
        except HTTPError as e:
            # Add Riot API-specific context to error message
            raise HTTPError(
                e.url,
                e.status_code,
                f"Riot API Error: {e.message}"
            ) from e

    # Replay control methods
    async def load(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = REPLAY_READY_RETRY_COUNT
    ) -> Dict[str, Any]:
        """Load and initialize replay.

        Args:
            timeout: Time to wait for replay to be ready (default: 30.0s)
            retries: Number of retry attempts (default: 10)

        Returns:
            Dictionary containing replay load status
        """
        return await self.request(
            "/replay/load",
            method="POST",
            body={"timeout": timeout},
            retries=retries
        )

    async def get_recording_properties(self) -> Dict[str, Any]:
        """Get current recording properties.

        Returns:
            Dictionary containing recording settings
        """
        return await self.request("/replay/recording")

    async def set_recording_properties(
        self,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set recording properties.

        Args:
            properties: Recording configuration to set

        Returns:
            Dictionary containing updated recording settings
        """
        return await self.request(
            "/replay/recording",
            method="POST",
            body=properties
        )

    async def get_render_properties(self) -> Dict[str, Any]:
        """Get current render properties.

        Returns:
            Dictionary containing render settings
        """
        return await self.request("/replay/render")

    async def set_render_properties(
        self,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set render properties.

        Args:
            properties: Render configuration to set

        Returns:
            Dictionary containing updated render settings
        """
        return await self.request(
            "/replay/render",
            method="POST",
            body=properties
        )

    async def start_recording(self) -> Dict[str, Any]:
        """Start recording the replay.

        Returns:
            Dictionary containing recording status
        """
        return await self.request("/replay/recording/start", method="POST")

    async def stop_recording(self) -> Dict[str, Any]:
        """Stop recording the replay.

        Returns:
            Dictionary containing recording status
        """
        return await self.request("/replay/recording/stop", method="POST")

    async def pause(self) -> Dict[str, Any]:
        """Pause replay playback.

        Returns:
            Dictionary containing playback status
        """
        return await self.request("/replay/pause", method="POST")

    async def resume(self) -> Dict[str, Any]:
        """Resume replay playback.

        Returns:
            Dictionary containing playback status
        """
        return await self.request("/replay/resume", method="POST")

    async def seek(self, time: float) -> Dict[str, Any]:
        """Seek to specific time in replay.

        Args:
            time: Time in seconds to seek to

        Returns:
            Dictionary containing playback status
        """
        return await self.request(
            "/replay/seek",
            method="POST",
            body={"time": time}
        )

    async def get_game_data(self) -> Dict[str, Any]:
        """Get current game data.

        Returns:
            Dictionary containing game information
        """
        return await self.request("/replay/gameData")

    async def get_playback_info(self) -> Dict[str, Any]:
        """Get current playback information.

        Returns:
            Dictionary containing playback data (current time, duration, etc.)
        """
        return await self.request("/replay/playback")

    async def focus_summoner(self, summoner_name: str) -> Dict[str, Any]:
        """Focus camera on specific summoner.

        Args:
            summoner_name: Name of the summoner to focus on

        Returns:
            Dictionary containing camera status
        """
        return await self.request(
            "/replay/focus",
            method="POST",
            body={"summonerName": summoner_name}
        )

    async def get_thumbnail(self, time: float) -> bytes:
        """Get thumbnail image at specific time.

        Args:
            time: Time in seconds for thumbnail

        Returns:
            Raw image bytes
        """
        # This endpoint returns binary data, not JSON
        url = f"{self.base_url}/replay/thumbnail"

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params={"time": time}
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            raise HTTPError(url, 0, f"Failed to get thumbnail: {str(e)}")

    
    async def wait_for_ready(self, timeout: float = REPLAY_READY_TIMEOUT, check_interval: float = REPLAY_READY_CHECK_INTERVAL) -> bool:
        """Wait for the replay API to be ready.

        Args:
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds

        Returns:
            True if API is ready, False if timeout reached
        """
        import asyncio

        elapsed = 0.0
        while elapsed < timeout:
            try:
                # Simple health check - try to get playback info
                await self.get_playback_info()
                return True
            except HTTPError:
                # API not ready yet, continue waiting
                pass

            await asyncio.sleep(check_interval)
            elapsed += check_interval

        return False

    async def exit(self) -> None:
        """Exit the replay process.

        This should be called when done with the replay to properly
        clean up resources.
        """
        try:
            await self.request("/replay/exit", method="POST")
        except HTTPError:
            # Don't raise errors on exit - the process might already be gone
            pass