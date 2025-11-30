import pytest
from unittest.mock import AsyncMock, patch, mock_open, MagicMock
from pathlib import Path
from lol_replay_recorder.clients.http.lcu import LCUClient
from lol_replay_recorder.models import make_lcu_request, read_lockfile


@pytest.mark.asyncio
@pytest.mark.unit
async def test_read_lockfile_success():
    lockfile_content = "LeagueClient:12345:54321:mypassword:https"

    # Mock Path.exists() to return True and Path.read_text() to return the lockfile content
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.read_text", return_value=lockfile_content):
        result = await read_lockfile("/fake/path/lockfile")
        assert result["port"] == "54321"
        assert result["password"] == "mypassword"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_make_lcu_request_uses_lockfile_credentials():
    lockfile_content = "LeagueClient:12345:54321:mypassword:https"

    # Create a regular mock for the response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json.return_value = {"data": "test"}

    # Mock Path.exists() and Path.read_text() for read_lockfile
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.read_text", return_value=lockfile_content):

        # Mock the httpx.AsyncClient context manager and its request method
        with patch("httpx.AsyncClient") as mock_client_class:
            # Create a mock instance that will be returned by the context manager
            mock_client_instance = AsyncMock()
            mock_client_instance.request.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance

            result = await make_lcu_request(
                "/fake/lockfile",
                "/test/endpoint",
                "GET"
            )
            assert result == {"data": "test"}
            # Verify that client.request was called with correct parameters
            mock_client_instance.request.assert_called_once_with(
                method="GET",
                url="https://127.0.0.1:54321/test/endpoint",
                headers={
                    "Authorization": "Basic cmlvdDpteXBhc3N3b3Jk",
                    "Content-Type": "application/json",
                },
                json=None,
            )