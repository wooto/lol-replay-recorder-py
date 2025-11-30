import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from lol_replay_recorder.controllers.league_client import LeagueClient
from lol_replay_recorder.controllers.league_client_ux import LeagueClientUx
from lol_replay_recorder.controllers.riot_game_client import RiotGameClient
from lol_replay_recorder.controllers.league_replay_client import LeagueReplayClient
from lol_replay_recorder.models.locale import Locale
from lol_replay_recorder.models.riot_types import Region, PlatformId
from lol_replay_recorder.domain.errors import CustomError
from lol_replay_recorder.services.config.editors.yaml import YamlEditor
from lol_replay_recorder.services.config.editors.ini import IniEditor


class TestLeagueClient:
    """Test cases for LeagueClient orchestrator."""

    @pytest.fixture
    def league_client(self):
        """Create a LeagueClient instance for testing."""
        return LeagueClient()

    @pytest.fixture
    def mock_subprocess(self):
        """Mock subprocess for process management."""
        with patch('lol_replay_recorder.controllers.league_client.subprocess') as mock:
            mock.run.return_value.returncode = 0
            mock.run.return_value.stdout = ""
            mock.run.return_value.stderr = ""
            yield mock

    @pytest.fixture
    def mock_asyncio_subprocess(self):
        """Mock asyncio subprocess for async operations."""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            yield mock_process

    @pytest.fixture
    def mock_yaml_editor(self):
        """Mock YamlEditor."""
        with patch('lol_replay_recorder.controllers.league_client.YamlEditor') as mock:
            mock_instance = MagicMock()
            mock_instance.data = {
                "locale_data": {
                    "available_locales": ["en_US", "ko_KR"],
                    "default_locale": "en_US"
                },
                "settings": {
                    "locale": "en_US"
                }
            }
            mock.return_value = mock_instance
            yield mock

    @pytest.fixture
    def mock_ini_editor(self):
        """Mock IniEditor."""
        with patch('lol_replay_recorder.controllers.league_client.IniEditor') as mock:
            mock_instance = MagicMock()
            mock_instance.data = {
                "config": {
                    "General": {
                        "EnableReplayApi": 1
                    }
                }
            }
            mock.return_value = mock_instance
            yield mock

    @pytest.mark.unit
    def test_init(self, league_client):
        """Test LeagueClient initialization."""
        assert league_client.riot_game_client is None
        assert league_client.league_client_ux is None
        assert league_client.league_replay_client is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_start_riot_processes_safely_success(self, league_client, mock_asyncio_subprocess):
        """Test successful start of Riot processes."""
        params = {
            "region": PlatformId.NA,
            "locale": Locale.en_US,
            "username": "test_user",
            "password": "test_pass"
        }

        # Mock sub-components
        mock_riot_client = AsyncMock()
        mock_league_ux = AsyncMock()
        mock_league_ux.get_region_locale.return_value = {"locale": "en_US", "region": "na"}
        mock_league_ux.get_state.return_value = {"action": "Idle"}

        with patch('lol_replay_recorder.controllers.league_client.RiotGameClient', return_value=mock_riot_client):
            with patch('lol_replay_recorder.controllers.league_client.LeagueClientUx', return_value=mock_league_ux):
                with patch.object(league_client, 'stop_riot_processes') as mock_stop:
                    with patch.object(league_client, 'set_locale') as mock_set_locale:
                        await league_client.start_riot_processes_safely(params)

                        # Verify all steps were called
                        mock_stop.assert_called_once()
                        mock_set_locale.assert_called_once_with(Locale.en_US)
                        mock_riot_client.start_riot_client.assert_called_once()
                        mock_riot_client.login.assert_called_once_with("test_user", "test_pass", PlatformId.NA)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_start_riot_processes_safely_retry_logic(self, league_client, mock_asyncio_subprocess):
        """Test retry logic when starting Riot processes."""
        params = {
            "region": PlatformId.NA,
            "locale": Locale.en_US,
            "username": "test_user",
            "password": "test_pass"
        }

        # Mock sub-components with failure then success
        mock_riot_client = AsyncMock()
        call_count = 0
        async def mock_start_riot_client(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Failed")
            return None
        mock_riot_client.start_riot_client.side_effect = mock_start_riot_client
        mock_league_ux = AsyncMock()
        mock_league_ux.get_region_locale.return_value = {"locale": "en_US", "region": "na"}
        mock_league_ux.get_state.side_effect = [{"action": "Busy"}, {"action": "Idle"}]

        with patch('lol_replay_recorder.controllers.league_client.RiotGameClient', return_value=mock_riot_client):
            with patch('lol_replay_recorder.controllers.league_client.LeagueClientUx', return_value=mock_league_ux):
                with patch.object(league_client, 'stop_riot_processes') as mock_stop:
                    with patch.object(league_client, 'set_locale') as mock_set_locale:
                        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                            await league_client.start_riot_processes_safely(params)

                            # Should retry at least once
                            assert mock_sleep.call_count >= 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_start_riot_processes_safely_locale_mismatch(self, league_client, mock_asyncio_subprocess):
        """Test locale mismatch error when starting Riot processes."""
        params = {
            "region": PlatformId.NA,
            "locale": Locale.en_US,
            "username": "test_user",
            "password": "test_pass"
        }

        # Mock sub-components with wrong locale
        mock_riot_client = AsyncMock()
        mock_league_ux = AsyncMock()
        mock_league_ux.get_region_locale.return_value = {"locale": "ko_KR", "region": "na"}  # Wrong locale
        mock_league_ux.get_state.return_value = {"action": "Idle"}

        with patch('lol_replay_recorder.controllers.league_client.RiotGameClient', return_value=mock_riot_client):
            with patch('lol_replay_recorder.controllers.league_client.LeagueClientUx', return_value=mock_league_ux):
                with patch.object(league_client, 'stop_riot_processes'):
                    with patch.object(league_client, 'set_locale'):
                        with pytest.raises(CustomError, match="Locale is not correct"):
                            await league_client.start_riot_processes_safely(params)

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_stop_riot_processes_windows(self, league_client, mock_subprocess):
        """Test stopping Riot processes on Windows."""
        with patch('platform.system', return_value='Windows'):
            # Mock tasklist to show processes are running then not running
            mock_subprocess.run.side_effect = [
                MagicMock(returncode=0, stdout="RiotClientUx.exe\n"),  # First check - process running
                MagicMock(returncode=1),  # Second check - process not found
                MagicMock(returncode=0, stdout="LeagueClient.exe\n"),  # Third check - process running
                MagicMock(returncode=1),  # Fourth check - process not found
            ]

            await league_client.stop_riot_processes()

            # Should attempt to kill processes
            assert mock_subprocess.run.call_count >= 2

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_stop_riot_processes_unix(self, league_client):
        """Test stopping Riot processes on Unix systems."""
        with patch('platform.system', return_value='Darwin'):
            mock_popen = MagicMock()
            mock_popen.communicate.return_value = (b"", b"")
            mock_popen.returncode = 0

            with patch('subprocess.Popen', return_value=mock_popen):
                with patch('asyncio.sleep', new_callable=AsyncMock):
                    await league_client.stop_riot_processes()

    @pytest.mark.unit
    def test_get_installed_paths(self, league_client):
        """Test getting installed paths."""
        with patch.object(league_client.platform_resolver, 'get_installed_paths', return_value=["C:\\Riot Games\\League of Legends"]):
            paths = league_client.get_installed_paths()
            assert paths == ["C:\\Riot Games\\League of Legends"]

    @pytest.mark.unit
    def test_get_config_file_paths(self, league_client):
        """Test getting config file paths."""
        with patch.object(league_client.platform_resolver, 'get_installed_paths', return_value=["C:\\Riot Games\\League of Legends"]):
            with patch.object(league_client.platform_resolver, 'get_config_file_path', return_value="C:\\Riot Games\\League of Legends\\Config\\game.cfg"):
                paths = league_client.get_config_file_paths()
                assert paths == ["C:\\Riot Games\\League of Legends\\Config\\game.cfg"]

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_config_file_path_success(self, league_client):
        """Test successful config file path resolution."""
        initial_path = "C:\\Riot Games\\League of Legends"
        with patch('os.path.exists', side_effect=lambda path: "Config" in path):
            config_path = league_client.get_config_file_path(initial_path)
            assert "game.cfg" in config_path

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_config_file_path_not_found(self, league_client):
        """Test config file path not found."""
        initial_path = "C:\\Nonexistent\\Path"
        with patch('os.path.exists', return_value=False):
            config_path = league_client.get_config_file_path(initial_path)
            assert config_path is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_is_game_enabled_true(self, league_client, mock_ini_editor):
        """Test checking if replay API is enabled (true case)."""
        mock_ini_editor.return_value.data["config"]["General"]["EnableReplayApi"] = 1
        result = await league_client.is_game_enabled("test_path")
        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_is_game_enabled_false(self, league_client, mock_ini_editor):
        """Test checking if replay API is enabled (false case)."""
        mock_ini_editor.return_value.data["config"]["General"]["EnableReplayApi"] = 0
        result = await league_client.is_game_enabled("test_path")
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_is_game_enabled_error(self, league_client, mock_ini_editor):
        """Test checking if replay API is enabled with error."""
        mock_ini_editor.side_effect = Exception("Config file not found")
        result = await league_client.is_game_enabled("invalid_path")
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_set_game_enabled(self, league_client, mock_ini_editor):
        """Test setting replay API enabled/disabled."""
        await league_client.set_game_enabled("test_path", True)
        mock_ini_editor.assert_called_once_with("test_path")
        mock_ini_editor.return_value.update_section.assert_called_once_with("General", "EnableReplayApi", True)
        mock_ini_editor.return_value.save.assert_called_once()

    def test_get_game_input_ini_path_windows(self, league_client):
        """Test getting game input.ini path on Windows."""
        with patch.object(league_client.platform_resolver, 'is_windows', return_value=True):
            path = league_client.get_game_input_ini_path()
            assert "input.ini" in path
            assert "Config" in path

    def test_get_game_input_ini_path_unix(self, league_client):
        """Test getting game input.ini path on Unix systems."""
        with patch.object(league_client.platform_resolver, 'is_windows', return_value=False):
            with patch.object(league_client.platform_resolver, 'is_macos', return_value=True):
                path = league_client.get_game_input_ini_path()
                assert "input.ini" in path

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_set_default_input_ini(self, league_client, mock_ini_editor):
        """Test setting default input.ini configuration."""
        with patch.object(league_client, 'get_game_input_ini_path', return_value="test_input.ini"):
            await league_client.set_default_input_ini()

            # Verify all required key bindings are set
            expected_calls = [
                ("GameEvents", "evtSelectOrderPlayer1", "[1]"),
                ("GameEvents", "evtSelectOrderPlayer2", "[2]"),
                ("GameEvents", "evtSelectOrderPlayer3", "[3]"),
                ("GameEvents", "evtSelectOrderPlayer4", "[4]"),
                ("GameEvents", "evtSelectOrderPlayer5", "[5]"),
            ]

            for section, key, value in expected_calls:
                mock_ini_editor.return_value.update_section.assert_any_call(section, key, value)

            mock_ini_editor.return_value.save.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_set_locale_success(self, league_client, mock_yaml_editor):
        """Test successfully setting locale."""
        await league_client.set_locale("en_US")
        mock_yaml_editor.return_value.update.assert_any_call("locale_data.default_locale", "en_US")
        mock_yaml_editor.return_value.update.assert_any_call("settings.locale", "en_US")
        mock_yaml_editor.return_value.save_changes.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_set_locale_invalid(self, league_client, mock_yaml_editor):
        """Test setting invalid locale."""
        mock_yaml_editor.return_value.data["locale_data"]["available_locales"] = ["en_US", "ko_KR"]

        with pytest.raises(CustomError, match="Invalid locale"):
            await league_client.set_locale("invalid_locale")

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_focus_client_window(self, league_client):
        """Test focusing client window."""
        mock_window_handler = AsyncMock()
        league_client._window_handler = mock_window_handler

        with patch.object(league_client.platform_resolver, 'is_windows', return_value=True):
            await league_client.focus_client_window()
            mock_window_handler.focus_client_window.assert_called_once_with("League of Legends (TM)")

    @pytest.mark.unit
    def test_get_product_settings_path_windows(self, league_client):
        """Test getting product settings path on Windows."""
        with patch.object(league_client.platform_resolver, 'get_product_settings_path',
                        return_value="C:\\ProgramData\\Riot Games\\Metadata\\league_of_legends.live\\league_of_legends.live.product_settings.yaml"):
            path = league_client.get_product_settings_path()
            assert "product_settings.yaml" in path
            assert "ProgramData" in path

    @pytest.mark.unit
    def test_get_product_settings_path_unix(self, league_client):
        """Test getting product settings path on Unix systems."""
        with patch.object(league_client.platform_resolver, 'is_windows', return_value=False):
            path = league_client.get_product_settings_path()
            assert "product_settings.yaml" in path
            assert ".config" in path  # Unix systems use .config directory

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_initialize_components(self, league_client):
        """Test lazy initialization of component controllers."""
        # Components should be None initially
        assert league_client.riot_game_client is None
        assert league_client.league_client_ux is None
        assert league_client.league_replay_client is None

        # Access properties to trigger lazy initialization
        riot_client = league_client.get_riot_game_client()
        league_ux = league_client.get_league_client_ux()
        replay_client = league_client.get_league_replay_client()

        # Components should be initialized
        assert isinstance(riot_client, RiotGameClient)
        assert isinstance(league_ux, LeagueClientUx)
        assert isinstance(replay_client, LeagueReplayClient)

        # Second access should return same instances
        assert league_client.get_riot_game_client() is riot_client
        assert league_client.get_league_client_ux() is league_ux
        assert league_client.get_league_replay_client() is replay_client

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_comprehensive_workflow(self, league_client):
        """Test a comprehensive workflow using multiple components."""
        # Mock all components
        mock_riot_client = AsyncMock()
        mock_league_ux = AsyncMock()
        mock_replay_client = AsyncMock()
        mock_window_handler = AsyncMock()

        league_client.riot_game_client = mock_riot_client
        league_client.league_client_ux = mock_league_ux
        league_client.league_replay_client = mock_replay_client
        league_client._window_handler = mock_window_handler

        # Test a typical workflow
        await league_client.focus_client_window()

        # Verify window handler was used
        mock_window_handler.focus_client_window.assert_called_once()

        # Test component access through properties
        assert league_client.get_riot_game_client() is mock_riot_client
        assert league_client.get_league_client_ux() is mock_league_ux
        assert league_client.get_league_replay_client() is mock_replay_client