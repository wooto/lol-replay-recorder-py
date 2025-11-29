import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from lol_replay_recorder.controllers.league_client_ux import LeagueClientUx
from lol_replay_recorder.models.locale import Locale
from lol_replay_recorder.models.riot_types import PlatformId
from lol_replay_recorder.models.summoner import Summoner
from lol_replay_recorder.models.custom_error import CustomError


class TestLeagueClientUx:
    """Test cases for LeagueClientUx controller."""

    @pytest.fixture
    def league_client_ux(self):
        """Create a LeagueClientUx instance for testing."""
        return LeagueClientUx(lockfile_path="/test/lockfile")

    @pytest.fixture
    def mock_lockfile_path(self):
        """Create a temporary lockfile for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.lockfile') as f:
            f.write("LeagueClient:1234:5678:password:https")
            lockfile_path = f.name

        yield lockfile_path

        try:
            os.unlink(lockfile_path)
        except FileNotFoundError:
            pass

    @pytest.fixture
    def mock_lcu_request(self):
        """Mock LCU request function."""
        with patch('lol_replay_recorder.controllers.league_client_ux.make_lcu_request') as mock:
            yield mock

    @pytest.fixture
    def mock_asyncio_create_subprocess(self):
        """Mock asyncio.create_subprocess_exec."""
        with patch('asyncio.create_subprocess_exec') as mock:
            yield mock

    @pytest.fixture
    def mock_pygetwindow(self):
        """Mock pygetwindow."""
        with patch('lol_replay_recorder.controllers.window_handler._get_pygetwindow') as mock:
            yield mock

    def test_init(self, league_client_ux):
        """Test LeagueClientUx initialization."""
        assert league_client_ux.patch == ""
        assert league_client_ux.lockfile_path == "/test/lockfile"

    @pytest.mark.asyncio
    async def test_get_lockfile_path_windows(self):
        """Test getting lockfile path on Windows."""
        client = LeagueClientUx()
        with patch('platform.system', return_value='Windows'):
            with patch('os.path.join', return_value='C:\\Users\\Test\\AppData\\Local\\Riot Games\\League of Legends\\lockfile'):
                with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local'}):
                    lockfile_path = await client.get_lockfile_path()
                    expected_path = 'C:\\Users\\Test\\AppData\\Local\\Riot Games\\League of Legends\\lockfile'
                    assert lockfile_path == expected_path

    @pytest.mark.asyncio
    async def test_get_lockfile_path_unix(self):
        """Test getting lockfile path on Unix systems."""
        client = LeagueClientUx()
        with patch.dict(os.environ, {}, clear=False):
            with patch('platform.system', return_value='Darwin'):
                lockfile_path = await client.get_lockfile_path()
                expected_path = os.path.expanduser('~/Library/Application Support/Riot Games/League of Legends/lockfile')
                assert lockfile_path == expected_path

    @pytest.mark.asyncio
    async def test_remove_lockfile_success(self, mock_lockfile_path):
        """Test successful lockfile removal."""
        league_client_ux = LeagueClientUx(lockfile_path=mock_lockfile_path)

        # Verify file exists
        assert os.path.exists(mock_lockfile_path)

        await league_client_ux.remove_lockfile()

        # Verify file was removed
        assert not os.path.exists(mock_lockfile_path)

    @pytest.mark.asyncio
    async def test_remove_lockfile_not_exists(self, league_client_ux):
        """Test removing non-existent lockfile (should not raise error)."""
        league_client_ux.lockfile_path = "/non/existent/path.lock"

        # Should not raise an exception
        await league_client_ux.remove_lockfile()

    @pytest.mark.asyncio
    async def test_wait_for_client_to_be_ready_success(self, league_client_ux, mock_lcu_request):
        """Test successful client readiness check."""
        mock_lcu_request.return_value = {"action": "Idle"}

        result = await league_client_ux.wait_for_client_to_be_ready()

        assert result is True
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-patch/v1/products/league_of_legends/state',
            'GET',
            None,
            0
        )

    @pytest.mark.asyncio
    async def test_wait_for_client_to_be_ready_timeout(self, league_client_ux, mock_lcu_request):
        """Test client readiness check timeout."""
        mock_lcu_request.side_effect = Exception("Client not ready")

        with pytest.raises(CustomError, match="League Client took too long to start"):
            await league_client_ux.wait_for_client_to_be_ready()

    @pytest.mark.asyncio
    async def test_get_highlights_folder_path(self, league_client_ux, mock_lcu_request):
        """Test getting highlights folder path."""
        expected_path = "C:\\Highlights"
        mock_lcu_request.return_value = expected_path

        result = await league_client_ux.get_highlights_folder_path()

        assert result == expected_path
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-highlights/v1/highlights-folder-path',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_get_game_settings(self, league_client_ux, mock_lcu_request):
        """Test getting game settings."""
        expected_settings = {"General": {"WindowMode": 1}}
        mock_lcu_request.return_value = expected_settings

        result = await league_client_ux.get_game_settings()

        assert result == expected_settings
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-game-settings/v1/game-settings'
        )

    @pytest.mark.asyncio
    async def test_get_input_settings(self, league_client_ux, mock_lcu_request):
        """Test getting input settings."""
        expected_settings = {"Camera": {"MovementSpeed": 50}}
        mock_lcu_request.return_value = expected_settings

        result = await league_client_ux.get_input_settings()

        assert result == expected_settings
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-game-settings/v1/input-settings'
        )

    @pytest.mark.asyncio
    async def test_get_region_locale(self, league_client_ux, mock_lcu_request):
        """Test getting region and locale."""
        expected_data = {"region": "na", "locale": "en_US"}
        mock_lcu_request.return_value = expected_data

        result = await league_client_ux.get_region_locale(5)

        assert result == expected_data
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/riotclient/region-locale',
            retries=5
        )

    @pytest.mark.asyncio
    async def test_patch_game_settings(self, league_client_ux, mock_lcu_request):
        """Test patching game settings."""
        settings_resource = {"General": {"WindowMode": 0}}
        expected_result = {"success": True}
        mock_lcu_request.return_value = expected_result

        result = await league_client_ux.patch_game_settings(settings_resource)

        assert result == expected_result
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-game-settings/v1/game-settings',
            method='PATCH',
            body=settings_resource
        )

    @pytest.mark.asyncio
    async def test_save_game_settings(self, league_client_ux, mock_lcu_request):
        """Test saving game settings."""
        mock_lcu_request.return_value = True

        result = await league_client_ux.save_game_settings()

        assert result is True
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-game-settings/v1/save',
            method='POST'
        )

    @pytest.mark.asyncio
    async def test_disable_window_mode_success(self, league_client_ux, mock_lcu_request):
        """Test successfully disabling window mode."""
        mock_lcu_request.side_effect = [
            {"success": True},  # patch_game_settings
            True  # save_game_settings
        ]

        result = await league_client_ux.disable_window_mode()

        assert result["success"] is True
        assert mock_lcu_request.call_count == 2

    @pytest.mark.asyncio
    async def test_disable_window_mode_failure(self, league_client_ux, mock_lcu_request):
        """Test failing to disable window mode."""
        mock_lcu_request.side_effect = [
            {"success": True},  # patch_game_settings
            False  # save_game_settings
        ]

        with pytest.raises(CustomError, match="Failed to disable windowed mode"):
            await league_client_ux.disable_window_mode()

    @pytest.mark.asyncio
    async def test_enable_window_mode_success(self, league_client_ux, mock_lcu_request):
        """Test successfully enabling window mode."""
        mock_lcu_request.side_effect = [
            {"success": True},  # patch_game_settings
            True  # save_game_settings
        ]

        result = await league_client_ux.enable_window_mode()

        assert result["success"] is True
        assert mock_lcu_request.call_count == 2

    @pytest.mark.asyncio
    async def test_get_replay_config(self, league_client_ux, mock_lcu_request):
        """Test getting replay configuration."""
        expected_config = {"downloadLocation": "C:\\Replays"}
        mock_lcu_request.return_value = expected_config

        result = await league_client_ux.get_replay_config()

        assert result == expected_config
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-replays/v1/configuration'
        )

    @pytest.mark.asyncio
    async def test_get_replay_metadata(self, league_client_ux, mock_lcu_request):
        """Test getting replay metadata."""
        match_id = "NA1_123456789"
        expected_metadata = {"state": "watch", "downloadProgress": 100}
        mock_lcu_request.return_value = expected_metadata

        result = await league_client_ux.get_replay_metadata(match_id)

        assert result == expected_metadata
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            f'/lol-replays/v1/metadata/{match_id}'
        )

    @pytest.mark.asyncio
    async def test_get_rofls_path(self, league_client_ux, mock_lcu_request):
        """Test getting ROFLs path."""
        expected_path = "C:\\Riot Games\\League of Legends\\Replays"
        mock_lcu_request.return_value = expected_path

        result = await league_client_ux.get_rofls_path()

        assert result == expected_path
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-replays/v1/rofls/path',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_download_replay_success(self, league_client_ux, mock_lcu_request):
        """Test successful replay download."""
        match_id = "NA1_123456789"

        # Mock the download request and get_replay_metadata calls
        mock_lcu_request.side_effect = [
            None,  # download request
            {"state": "checking"},  # metadata check 1
            {"state": "downloading"},  # metadata check 2
            {"state": "watch"}  # final metadata check
        ]

        result = await league_client_ux.download_replay(match_id)

        assert result is None
        assert mock_lcu_request.call_count == 4

    @pytest.mark.asyncio
    async def test_download_replay_failure(self, league_client_ux, mock_lcu_request):
        """Test failed replay download."""
        match_id = "NA1_123456789"

        mock_lcu_request.side_effect = [
            None,  # download request
            {"state": "failed"}  # metadata check
        ]

        with pytest.raises(CustomError, match="Failed to download replay"):
            await league_client_ux.download_replay(match_id)

    @pytest.mark.asyncio
    async def test_launch_replay(self, league_client_ux, mock_lcu_request):
        """Test launching replay."""
        match_id = "NA1_123456789"

        # Mock download_replay and watch request
        mock_lcu_request.side_effect = [
            {"state": "watch"},  # get_replay_metadata in download_replay
            None  # watch request
        ]

        with patch.object(league_client_ux, 'download_replay') as mock_download:
            mock_download.return_value = None

            await league_client_ux.launch_replay(match_id)

            mock_download.assert_called_once_with(match_id)
            # Verify watch request was called
            mock_lcu_request.assert_called_with(
                "/test/lockfile",
                f'/lol-replays/v1/rofls/{match_id}/watch',
                'POST',
                None,
                10
            )

    @pytest.mark.asyncio
    async def test_get_end_of_match_data(self, league_client_ux, mock_lcu_request):
        """Test getting end of match data."""
        match_id = "NA1_123456789"
        expected_data = {"gameId": match_id, "participants": []}
        mock_lcu_request.return_value = expected_data

        result = await league_client_ux.get_end_of_match_data_by_match_id(match_id)

        assert result == expected_data
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            f'/lol-match-history/v1/games/{match_id}',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_get_summoners_by_riot_id(self, league_client_ux, mock_lcu_request):
        """Test getting summoners by Riot ID."""
        riot_id = "Player#1234"
        expected_summoners = [{"summonerName": "Player", "tagLine": "1234"}]
        mock_lcu_request.return_value = expected_summoners

        result = await league_client_ux.get_summoners_by_riot_id(riot_id)

        assert result == expected_summoners
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            f'/lol-summoner/v1/summoners?name={riot_id}',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_get_match_history_by_puuid(self, league_client_ux, mock_lcu_request):
        """Test getting match history by PUUID."""
        puuid = "test-puuid-123"
        beg_index = 0
        end_index = 10
        expected_games = [{"gameId": "123"}, {"gameId": "456"}]

        mock_lcu_request.return_value = {
            "games": {"games": expected_games}
        }

        result = await league_client_ux.get_match_history_by_puuid(puuid, beg_index, end_index)

        assert result == expected_games
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            f'/lol-match-history/v1/products/lol/{puuid}/matches?begIndex={beg_index}&endIndex={end_index}',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_get_match_timeline_by_match_id(self, league_client_ux, mock_lcu_request):
        """Test getting match timeline by match ID."""
        match_id = "NA1_123456789"
        expected_frames = [{"timestamp": 1000}, {"timestamp": 2000}]

        mock_lcu_request.return_value = {"frames": expected_frames}

        result = await league_client_ux.get_match_timeline_by_match_id(match_id)

        assert result == expected_frames
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            f'/lol-match-history/v1/game-timelines/{match_id}',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_get_patch_version_cached(self, league_client_ux):
        """Test getting patch version when cached."""
        league_client_ux.patch = "13.5"

        result = await league_client_ux.get_patch_version()

        assert result == "13.5"

    @pytest.mark.asyncio
    async def test_get_patch_version_not_cached(self, league_client_ux, mock_lcu_request):
        """Test getting patch version when not cached."""
        expected_patch = "13.5.321.1234"
        mock_lcu_request.return_value = expected_patch

        result = await league_client_ux.get_patch_version()

        assert result == expected_patch
        assert league_client_ux.patch == expected_patch
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-patch/v1/game-version',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_get_state(self, league_client_ux, mock_lcu_request):
        """Test getting client state."""
        expected_state = {"action": "Idle"}
        mock_lcu_request.return_value = expected_state

        result = await league_client_ux.get_state({"retry": 5})

        assert result == expected_state
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-patch/v1/products/league_of_legends/state',
            'GET',
            None,
            5
        )

    @pytest.mark.asyncio
    async def test_get_queues(self, league_client_ux, mock_lcu_request):
        """Test getting game queues."""
        expected_queues = [{"queueId": 420, "name": "Ranked Solo/Duo"}]
        mock_lcu_request.return_value = expected_queues

        result = await league_client_ux.get_queues()

        assert result == expected_queues
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            'lol-game-queues/v1/queues',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_get_current_summoner(self, league_client_ux, mock_lcu_request):
        """Test getting current summoner."""
        summoner_data = {
            "displayName": "TestPlayer",
            "tagLine": "NA1",
            "puuid": "test-puuid-123"
        }
        mock_lcu_request.return_value = summoner_data

        result = await league_client_ux.get_current_summoner()

        assert isinstance(result, Summoner)
        assert result.summoner_name == "TestPlayer"
        assert result.tagline == "NA1"
        assert result.puuid == "test-puuid-123"
        mock_lcu_request.assert_called_once_with(
            "/test/lockfile",
            '/lol-summoner/v1/current-summoner',
            'GET',
            None,
            3
        )

    @pytest.mark.asyncio
    async def test_start_client_windows(self, mock_asyncio_create_subprocess):
        """Test starting League client on Windows."""
        client = LeagueClientUx()
        params = {
            "region": PlatformId.NA1,
            "locale": Locale.en_US
        }

        mock_process = AsyncMock()
        mock_asyncio_create_subprocess.return_value = mock_process

        with patch('platform.system', return_value='Windows'):
            await client.start_client(params)

            mock_asyncio_create_subprocess.assert_called_once()
            call_args = mock_asyncio_create_subprocess.call_args[0]

            # Check that the executable path is correct
            assert "LeagueClient.exe" in call_args[0]

            # Check that parameters are included
            args = call_args[1]
            assert any("--region=NA" in str(arg) for arg in args)
            assert any("--locale=en_US" in str(arg) for arg in args)

    @pytest.mark.asyncio
    async def test_start_client_macos(self, mock_asyncio_create_subprocess):
        """Test starting League client on macOS."""
        client = LeagueClientUx()
        params = {
            "region": PlatformId.NA1,
            "locale": Locale.en_US
        }

        mock_process = AsyncMock()
        mock_asyncio_create_subprocess.return_value = mock_process

        with patch('platform.system', return_value='Darwin'):
            with patch('os.path.exists', return_value=True):
                await client.start_client(params)

                mock_asyncio_create_subprocess.assert_called_once()
                call_args = mock_asyncio_create_subprocess.call_args[0]

                # Check that the app path is correct for macOS
                assert "League of Legends.app" in call_args[0] or "LeagueClient" in call_args[0]

    @pytest.mark.asyncio
    async def test_focus_client_window_success(self, mock_pygetwindow):
        """Test successfully focusing client window."""
        league_client_ux = LeagueClientUx()
        mock_window = MagicMock()
        mock_window.title = "League of Legends"
        mock_window.activate = MagicMock()

        # Set up the mock to return a mock gw module
        mock_gw_module = MagicMock()
        mock_gw_module.getWindowsWithTitle.return_value = [mock_window]
        mock_pygetwindow.return_value = mock_gw_module

        with patch('lol_replay_recorder.controllers.window_handler._get_pyautogui') as mock_pyautogui:
            await league_client_ux.focus_client_window()

            mock_gw_module.getWindowsWithTitle.assert_called_once_with("League of Legends")

    @pytest.mark.asyncio
    async def test_focus_client_window_failure(self, mock_pygetwindow):
        """Test failing to focus client window."""
        league_client_ux = LeagueClientUx()

        # Set up the mock to return a mock gw module with no windows
        mock_gw_module = MagicMock()
        mock_gw_module.getWindowsWithTitle.return_value = []
        mock_pygetwindow.return_value = mock_gw_module

        # Should not raise an exception, just print error
        await league_client_ux.focus_client_window()