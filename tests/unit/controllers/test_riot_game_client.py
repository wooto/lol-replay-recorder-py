import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, mock_open
from pathlib import Path

from lol_replay_recorder.controllers.riot_game_client import RiotGameClient
from lol_replay_recorder.models.locale import Locale
from lol_replay_recorder.models.riot_types import Region


@pytest.fixture
def riot_client():
    """Create a RiotGameClient instance for testing."""
    return RiotGameClient()


@pytest.mark.unit
def test_riot_game_client_initialization(riot_client):
    """Test RiotGameClient initialization."""
    assert riot_client.riot_client_services_path == '"C:\\Riot Games\\Riot Client\\RiotClientServices.exe"'
    assert riot_client.default_client_paths == ['C:\\Riot Games\\Riot Client']


@pytest.mark.asyncio
@pytest.mark.unit
async def test_is_running(riot_client):
    """Test checking if Riot client is running."""
    mock_response = {"action": "running"}

    with patch.object(riot_client, '_invoke_riot_request', return_value=mock_response):
        result = await riot_client.is_running()
        assert result == mock_response


@pytest.mark.asyncio
@pytest.mark.unit
async def test_login(riot_client):
    """Test login functionality."""
    with patch.object(riot_client, 'focus_client_window') as mock_focus:
        with patch('lol_replay_recorder.controllers.riot_game_client.sleep_in_seconds') as mock_sleep:
            with patch.object(riot_client, '_get_window_handler') as mock_handler:
                mock_window_handler = AsyncMock()
                mock_handler.return_value = mock_window_handler

                await riot_client.login("testuser", "testpass", "NA1")

                # Verify window focus
                mock_focus.assert_called_once()

                # Verify keyboard interactions (should be called many times)
                assert mock_window_handler.keyboard_type.call_count >= 29
                assert mock_window_handler.press_key.call_count >= 7


@pytest.mark.asyncio
@pytest.mark.unit
async def test_is_auto_login_enabled(riot_client):
    """Test checking if auto login is enabled."""
    mock_response = {"enabled": True}

    with patch.object(riot_client, '_invoke_riot_request', return_value=mock_response):
        result = await riot_client.is_auto_login_enabled()
        assert result == mock_response


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_state(riot_client):
    """Test getting client state."""
    mock_response = {"action": "launched"}

    with patch.object(riot_client, '_invoke_riot_request', return_value=mock_response):
        result = await riot_client.get_state()
        assert result == mock_response


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_installs(riot_client):
    """Test getting installation information."""
    mock_response = {"installs": [{"product": "league_of_legends"}]}

    with patch.object(riot_client, '_invoke_riot_request', return_value=mock_response):
        result = await riot_client.get_installs()
        assert result == mock_response


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_client_path(riot_client):
    """Test getting client installation path."""
    # Test with existing path
    with patch('os.path.exists', return_value=True):
        result = await riot_client.get_client_path()
        assert result == ['C:\\Riot Games\\Riot Client']

    # Test with non-existing path
    with patch('os.path.exists', return_value=False):
        result = await riot_client.get_client_path()
        assert result == []


@pytest.mark.asyncio
@pytest.mark.unit
async def test_remove_lockfile(riot_client):
    """Test removing lockfile."""
    mock_lockfile_path = "C:\\path\\to\\lockfile"

    with patch.object(riot_client, 'get_lockfile_path', return_value=mock_lockfile_path):
        with patch('os.unlink') as mock_unlink:
            await riot_client.remove_lockfile()
            mock_unlink.assert_called_once_with(mock_lockfile_path)

    # Test when lockfile doesn't exist
    with patch.object(riot_client, 'get_lockfile_path', return_value=mock_lockfile_path):
        with patch('os.unlink', side_effect=FileNotFoundError):
            # Should not raise exception
            await riot_client.remove_lockfile()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_lockfile_path(riot_client):
    """Test getting lockfile path."""
    with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local'}):
        result = await riot_client.get_lockfile_path()
        expected = Path('C:\\Users\\Test\\AppData\\Local') / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile'
        assert result == str(expected)


@pytest.mark.unit
def test_get_lockfile_credentials(riot_client):
    """Test extracting credentials from lockfile."""
    mock_lockfile_content = "process:123:5678:password:other"

    with patch('builtins.open', mock_open(read_data=mock_lockfile_content)):
        result = riot_client.get_lockfile_credentials("test_path")
        assert result.port == "5678"
        assert result.password == "password"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_start_riot_client(riot_client):
    """Test starting Riot client."""
    mock_region = "NA"
    mock_locale = "en_US"

    with patch('asyncio.create_subprocess_shell') as mock_subprocess:
        mock_process = AsyncMock()
        mock_subprocess.return_value = mock_process

        with patch.object(riot_client, 'get_installs', return_value={"installs": []}):
            with patch.object(riot_client, 'wait_to_patch') as mock_wait:
                await riot_client.start_riot_client(mock_region, mock_locale)

                # Verify subprocess was called with correct arguments
                mock_subprocess.assert_called_once()
                call_args = mock_subprocess.call_args[0][0]
                assert '--launch-product=league_of_legends' in call_args
                assert '--launch-patchline=live' in call_args
                assert f'--region={mock_region.upper()}' in call_args
                assert f'--locale={mock_locale}' in call_args

                # Verify wait_to_patch was called
                mock_wait.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_wait_to_patch(riot_client):
    """Test waiting for patching to complete."""
    mock_status_response = {"patch": {"state": "up_to_date", "progress": {"progress": 100}}}

    with patch.object(riot_client, '_invoke_riot_request', return_value=mock_status_response):
        # Should exit immediately on first iteration
        await riot_client.wait_to_patch()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_wait_to_patch_with_progress(riot_client):
    """Test waiting for patching with progress updates."""
    mock_in_progress = {"patch": {"state": "patching", "progress": {"progress": 50}}}
    mock_complete = {"patch": {"state": "up_to_date", "progress": {"progress": 100}}}

    with patch.object(riot_client, '_invoke_riot_request') as mock_request:
        mock_request.side_effect = [mock_in_progress, mock_complete]
        with patch('lol_replay_recorder.controllers.riot_game_client.sleep_in_seconds') as mock_sleep:
            await riot_client.wait_to_patch()
            # Should sleep once between checking status
            mock_sleep.assert_called_once_with(1)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_region_locale(riot_client):
    """Test getting region and locale information."""
    mock_response = {"locale": "en_US", "region": "na"}

    with patch.object(riot_client, '_invoke_riot_request', return_value=mock_response):
        result = await riot_client.get_region_locale(retry=3)
        assert result.locale == "en_US"
        assert result.region == "na"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_focus_client_window(riot_client):
    """Test focusing Riot client window."""
    with patch.object(riot_client, '_get_window_handler') as mock_handler:
        mock_window_handler = AsyncMock()
        mock_handler.return_value = mock_window_handler

        await riot_client.focus_client_window()

        mock_window_handler.focus_client_window.assert_called_once_with("Riot Client")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_wait_for_lockfile_exists(riot_client):
    """Test waiting for lockfile to exist."""
    mock_path = "test_lockfile"

    # Test when file exists immediately
    with patch('os.path.exists', return_value=True):
        # Should not raise exception
        await riot_client._wait_for_lockfile_exists(mock_path)

    # Test when file doesn't exist (timeout scenario)
    with patch('os.path.exists', return_value=False):
        with patch('lol_replay_recorder.controllers.riot_game_client.sleep_in_seconds', return_value=None):
            with pytest.raises(Exception, match="File not found"):
                await riot_client._wait_for_lockfile_exists(mock_path, timeout=2)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_invoke_riot_request(riot_client):
    """Test making authenticated requests to Riot client."""
    mock_lockfile_path = "test_lockfile"
    mock_lockfile_content = "process:123:5678:password:other"
    mock_response = {"data": "test"}

    with patch.object(riot_client, '_wait_for_lockfile_exists') as mock_wait:
        with patch('builtins.open', mock_open(read_data=mock_lockfile_content)):
            with patch('lol_replay_recorder.controllers.riot_game_client.RiotAPIClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.request_with_retry.return_value = mock_response
                mock_client_class.return_value = mock_client

                result = await riot_client._invoke_riot_request(
                    mock_lockfile_path,
                    '/test/path',
                    'POST',
                    {'test': 'data'},
                    retry=2
                )

                assert result == mock_response
                mock_client.request_with_retry.assert_called_once()

                # Verify request parameters
                call_args = mock_client.request_with_retry.call_args[1]  # kwargs
                assert call_args['method'] == 'POST'
                assert call_args['url'] == 'https://127.0.0.1:5678/test/path'
                assert 'Authorization' in call_args['headers']
                assert call_args['headers']['Authorization'].startswith('Basic ')
                assert call_args['body'] == {'test': 'data'}
                assert call_args['retries'] == 2


@pytest.mark.unit
def test_get_window_handler(riot_client):
    """Test getting window handler instance."""
    handler = riot_client._get_window_handler()
    assert handler is not None
    # Should return the same instance (singleton-like behavior)
    handler2 = riot_client._get_window_handler()
    assert handler is handler2