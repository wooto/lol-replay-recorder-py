"""Tests for new HTTP client implementations."""

import pytest
from unittest.mock import AsyncMock, patch, mock_open, MagicMock
from pathlib import Path

from lol_replay_recorder.clients.http.base import BaseHTTPClient
from lol_replay_recorder.clients.http.lcu import LCUClient
from lol_replay_recorder.clients.http.riot import RiotAPIClient
from lol_replay_recorder.domain.errors import HTTPError, LockfileError


class TestBaseHTTPClient:
    """Test BaseHTTPClient functionality."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_base_client_initialization(self):
        """Test BaseHTTPClient initialization."""
        client = BaseHTTPClient()
        assert client.verify_ssl is False
        assert client.timeout == 30.0

        client_custom = BaseHTTPClient(verify_ssl=True, timeout=60.0)
        assert client_custom.verify_ssl is True
        assert client_custom.timeout == 60.0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_request_with_retry_404_no_retry(self):
        """Test that 404 errors don't trigger retries."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.is_success = False

        client = BaseHTTPClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            mock_client_instance.request.return_value = mock_response

            with pytest.raises(HTTPError) as exc_info:
                await client.request_with_retry("GET", "https://test.com/api", retries=5)

            assert "Failed to find the requested resource" in str(exc_info.value)
            # Should only be called once, no retries for 404
            assert mock_client_instance.request.call_count == 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_request_with_retry_max_retries_exceeded(self):
        """Test max retries exceeded raises HTTPError."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.is_success = False

        client = BaseHTTPClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            mock_client_instance.request.return_value = mock_response

            with patch("asyncio.sleep") as mock_sleep:  # Speed up test
                with pytest.raises(HTTPError):
                    await client.request_with_retry("GET", "https://test.com/api", retries=2)

                # Should retry 2 times + initial call = 3 total
                assert mock_client_instance.request.call_count == 3
                assert mock_sleep.call_count == 2


class TestLCUClient:
    """Test LCUClient functionality."""

    def test_lcu_client_initialization(self):
        """Test LCU client initialization."""
        client = LCUClient()
        assert client.lockfile_path is None
        assert client.verify_ssl is False

        client_with_path = LCUClient(lockfile_path="/test/lockfile")
        assert client_with_path.lockfile_path == "/test/lockfile"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_read_lockfile_success(self):
        """Test successful lockfile reading."""
        lockfile_content = "LeagueClient:1234:5678:password:https"

        client = LCUClient()

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=lockfile_content):

            credentials = await client._read_lockfile("/test/lockfile")

            assert credentials["port"] == "5678"
            assert credentials["password"] == "password"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_read_lockfile_not_found(self):
        """Test lockfile not found raises LockfileError."""
        client = LCUClient()

        with patch("pathlib.Path.exists", return_value=False), \
             patch("asyncio.sleep"):  # Speed up test

            with pytest.raises(LockfileError) as exc_info:
                await client._read_lockfile("/nonexistent/lockfile")

            assert "Lockfile not found" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_read_lockfile_invalid_format(self):
        """Test invalid lockfile format raises LockfileError."""
        lockfile_content = "invalid:format"

        client = LCUClient()

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=lockfile_content):

            with pytest.raises(LockfileError) as exc_info:
                await client._read_lockfile("/test/lockfile")

            assert "Invalid lockfile format" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_lcu_request_success(self):
        """Test successful LCU request."""
        mock_response = {"data": "test"}

        client = LCUClient(lockfile_path="/test/lockfile")

        with patch.object(client, "_read_lockfile", return_value={"port": "5678", "password": "pass"}), \
             patch.object(client, "request_with_retry", return_value=mock_response) as mock_request:

            result = await client.request("/test/endpoint")

            assert result == mock_response
            mock_request.assert_called_once_with(
                method="GET",
                url="https://127.0.0.1:5678/test/endpoint",
                headers={
                    "Authorization": "Basic cmlvdDpwYXNz",
                    "Content-Type": "application/json"
                },
                body=None,
                retries=3,
                base_delay=0.1
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_lcu_request_no_lockfile(self):
        """Test LCU request without lockfile raises LockfileError."""
        client = LCUClient()  # No lockfile path set

        with pytest.raises(LockfileError) as exc_info:
            await client.request("/test/endpoint")

        assert "No lockfile path configured" in str(exc_info.value)


class TestRiotAPIClient:
    """Test RiotAPIClient functionality."""

    def test_riot_client_initialization(self):
        """Test Riot API client initialization."""
        client = RiotAPIClient()
        assert client.host == "127.0.0.1"
        assert client.port == 2999
        assert client.verify_ssl is False
        assert client.base_url == "https://127.0.0.1:2999"

        custom_client = RiotAPIClient(host="localhost", port=3000)
        assert custom_client.host == "localhost"
        assert custom_client.port == 3000
        assert custom_client.base_url == "https://localhost:3000"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_riot_request_success(self):
        """Test successful Riot API request."""
        mock_response = {"status": "ok"}

        client = RiotAPIClient()

        with patch.object(client, "request_with_retry", return_value=mock_response) as mock_request:
            result = await client.request("/replay/playback")

            assert result == mock_response
            mock_request.assert_called_once_with(
                method="GET",
                url="https://127.0.0.1:2999/replay/playback",
                headers=None,
                body=None,
                retries=5,
                base_delay=0.1
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_riot_request_with_body(self):
        """Test Riot API request with body."""
        mock_response = {"updated": True}
        request_body = {"key": "value"}

        client = RiotAPIClient()

        with patch.object(client, "request_with_retry", return_value=mock_response) as mock_request:
            result = await client.request("/replay/recording", method="POST", body=request_body)

            assert result == mock_response
            mock_request.assert_called_once_with(
                method="POST",
                url="https://127.0.0.1:2999/replay/recording",
                headers=None,
                body=request_body,
                retries=5,
                base_delay=0.1
            )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_convenience_methods(self):
        """Test convenience methods use correct endpoints."""
        mock_response = {"data": "test"}

        client = RiotAPIClient()

        with patch.object(client, "request", return_value=mock_response) as mock_request:
            # Test get_playback_info
            await client.get_playback_info()
            mock_request.assert_called_with("/replay/playback")

            # Test get_recording_properties
            await client.get_recording_properties()
            mock_request.assert_called_with("/replay/recording")

            # Test get_render_properties
            await client.get_render_properties()
            mock_request.assert_called_with("/replay/render")

            # Test get_game_data
            await client.get_game_data()
            mock_request.assert_called_with("/replay/gameData")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_wait_for_ready_success(self):
        """Test wait_for_ready returns True when API responds."""
        client = RiotAPIClient()

        with patch.object(client, "get_playback_info", return_value={"time": 100}):
            result = await client.wait_for_ready(timeout=1.0, check_interval=0.1)
            assert result is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_wait_for_ready_timeout(self):
        """Test wait_for_ready returns False on timeout."""
        client = RiotAPIClient()

        with patch.object(client, "get_playback_info", side_effect=HTTPError("", 0, "Connection failed")), \
             patch("asyncio.sleep"):  # Speed up test
            result = await client.wait_for_ready(timeout=0.1, check_interval=0.01)
            assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_exit_ignores_errors(self):
        """Test exit method ignores errors gracefully."""
        client = RiotAPIClient()

        with patch.object(client, "request", side_effect=HTTPError("", 0, "Already exited")):
            # Should not raise an exception
            await client.exit()