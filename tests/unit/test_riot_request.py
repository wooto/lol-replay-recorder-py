import pytest
from unittest.mock import AsyncMock, patch
from lol_replay_recorder.models.riot_request import make_request
from lol_replay_recorder.models.custom_error import CustomError


@pytest.mark.asyncio
async def test_make_request_success():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.is_success = True
    mock_response.json = AsyncMock(return_value={"data": "test"})

    with patch("httpx.AsyncClient.request", return_value=mock_response):
        result = await make_request("GET", "https://127.0.0.1:2999/test")
        assert result == {"data": "test"}


@pytest.mark.asyncio
async def test_make_request_404_raises_custom_error():
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.is_success = False

    with patch("httpx.AsyncClient.request", return_value=mock_response):
        with pytest.raises(CustomError) as exc_info:
            await make_request("GET", "https://127.0.0.1:2999/test", retries=0)
        assert "Failed to find the requested resource" in str(exc_info.value)


@pytest.mark.asyncio
async def test_make_request_retries_on_failure():
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.is_success = False

    with patch("httpx.AsyncClient.request", return_value=mock_response) as mock_req:
        with pytest.raises(Exception):
            await make_request("GET", "https://127.0.0.1:2999/test", retries=2)
        # Should retry 2 times + initial = 3 total calls
        assert mock_req.call_count >= 2