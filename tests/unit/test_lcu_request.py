import pytest
from unittest.mock import AsyncMock, patch, mock_open
from pathlib import Path
from lol_replay_recorder.models.lcu_request import (
    make_lcu_request,
    read_lockfile,
)


@pytest.mark.asyncio
async def test_read_lockfile_success():
    lockfile_content = "LeagueClient:12345:54321:mypassword:https"

    with patch("builtins.open", mock_open(read_data=lockfile_content)):
        result = await read_lockfile("/fake/path/lockfile")
        assert result["port"] == "54321"
        assert result["password"] == "mypassword"


@pytest.mark.asyncio
async def test_make_lcu_request_uses_lockfile_credentials():
    lockfile_content = "LeagueClient:12345:54321:mypassword:https"
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})

    with patch("builtins.open", mock_open(read_data=lockfile_content)):
        with patch("httpx.AsyncClient.request", return_value=mock_response) as mock_req:
            result = await make_lcu_request(
                "/fake/lockfile",
                "/test/endpoint",
                "GET"
            )
            assert result == {"data": "test"}
            # Verify authorization header was set
            call_kwargs = mock_req.call_args.kwargs
            assert "Authorization" in call_kwargs["headers"]