import pytest
from unittest.mock import AsyncMock, patch
from lol_replay_recorder.controllers.league_replay_client import LeagueReplayClient


@pytest.mark.asyncio
@pytest.mark.unit
async def test_league_replay_client_initialization():
    client = LeagueReplayClient()
    assert client.url == "https://127.0.0.1:2999"
    assert client.pid is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_playback_properties():
    client = LeagueReplayClient()

    mock_response = {"time": 100.0, "paused": False}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_playback_properties()
        assert result["time"] == 100.0
        mock_req.assert_called_once()
        assert mock_req.call_args[0][0] == "GET"
        assert mock_req.call_args[0][1] == "https://127.0.0.1:2999/replay/playback"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_recording_properties():
    client = LeagueReplayClient()

    mock_response = {"recording": True, "currentTime": 50.0}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_recording_properties()
        assert result["recording"] is True
        mock_req.assert_called_once()
        assert mock_req.call_args[0][0] == "GET"
        assert mock_req.call_args[0][1] == "https://127.0.0.1:2999/replay/recording"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_render_properties():
    client = LeagueReplayClient()

    mock_response = {"selectionName": "TestPlayer", "banners": True}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_render_properties()
        assert result["selectionName"] == "TestPlayer"
        mock_req.assert_called_once()
        assert mock_req.call_args[0][0] == "GET"
        assert mock_req.call_args[0][1] == "https://127.0.0.1:2999/replay/render"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_post_playback_properties():
    client = LeagueReplayClient()

    mock_response = {"time": 200.0}
    options = {"time": 200.0}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.post_playback_properties(options)
        assert result["time"] == 200.0
        mock_req.assert_called_once()
        assert mock_req.call_args[0][0] == "POST"
        assert mock_req.call_args[0][1] == "https://127.0.0.1:2999/replay/playback"
        assert mock_req.call_args[0][3] == options  # body parameter


@pytest.mark.asyncio
@pytest.mark.unit
async def test_set_and_get_process_id():
    client = LeagueReplayClient()

    # Test initial state
    assert client.pid is None

    # Test setting process ID
    client.set_process_id(12345)
    assert client.pid == 12345


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_process_id_from_api():
    client = LeagueReplayClient()

    mock_response = {"processID": 67890}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_process_id()
        assert result == 67890
        assert client.pid == 67890
        mock_req.assert_called_once()
        assert mock_req.call_args[0][0] == "GET"
        assert mock_req.call_args[0][1] == "https://127.0.0.1:2999/replay/game"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_all_game_data():
    client = LeagueReplayClient()

    mock_response = {"allPlayers": [], "gameData": {}}

    with patch("lol_replay_recorder.models.riot_request.make_request") as mock_req:
        mock_req.return_value = mock_response
        result = await client.get_all_game_data()
        assert result["allPlayers"] == []
        mock_req.assert_called_once()
        assert mock_req.call_args[0][0] == "GET"
        assert mock_req.call_args[0][1] == "https://127.0.0.1:2999/liveclientdata/allgamedata"