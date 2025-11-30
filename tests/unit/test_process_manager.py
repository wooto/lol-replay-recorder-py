"""ProcessManager unit tests."""

import os
import platform
import signal
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lol_replay_recorder.services.process.manager import ProcessManager
from lol_replay_recorder.services.process.platform import PlatformResolver
from lol_replay_recorder.domain.errors import CustomError, ProcessError


class TestProcessManager:
    """ProcessManager 클래스 단위 테스트."""

    def setup_method(self):
        """각 테스트 전에 실행되는 설정 메서드."""
        self.platform_resolver = MagicMock(spec=PlatformResolver)
        self.process_manager = ProcessManager(self.platform_resolver)

    @pytest.mark.asyncio
    async def test_start_safely_success(self):
        """성공적인 프로세스 시작 테스트."""
        # Mock dependencies
        params = {
            "region": "na",
            "locale": "en_US",
            "username": "test_user",
            "password": "test_pass"
        }

        with patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class:

            # Setup mocks
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # Mock successful flow
            mock_league_ux.get_state.return_value = {"action": "Idle"}
            mock_league_ux.get_region_locale.return_value = {"locale": "en_US"}

            # Execute
            await self.process_manager.start_safely(params)

            # Verify
            mock_riot_client.start_riot_client.assert_called_once_with("na", "en_US")
            mock_riot_client.login.assert_called_once_with("test_user", "test_pass", "na")
            mock_league_ux.wait_for_client_to_be_ready.assert_called_once()
            mock_league_ux.get_state.assert_called_once_with({"retry": 1})
            mock_league_ux.get_region_locale.assert_called_once_with(30)

    @pytest.mark.asyncio
    async def test_start_safely_retry_success(self):
        """재시도 후 성공하는 프로세스 시작 테스트."""
        params = {
            "region": "na",
            "locale": "en_US",
            "username": "test_user",
            "password": "test_pass"
        }

        with patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class, \
             patch('lol_replay_recorder.utils.utils.sleep_in_seconds') as mock_sleep:

            # Setup mocks
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # First attempt fails, second succeeds
            mock_riot_client.start_riot_client.side_effect = [Exception("Failed"), None]
            mock_league_ux.get_state.return_value = {"action": "Idle"}
            mock_league_ux.get_region_locale.return_value = {"locale": "en_US"}

            # Execute
            await self.process_manager.start_safely(params, max_attempts=2)

            # Verify
            assert mock_riot_client.start_riot_client.call_count == 2
            # Note: sleep is called via self.process_manager.stop_riot_processes() which is mocked internally

    @pytest.mark.asyncio
    async def test_start_safely_max_attempts_exceeded(self):
        """최대 시도 횟수 초과 시 실패 테스트."""
        params = {
            "region": "na",
            "locale": "en_US",
            "username": "test_user",
            "password": "test_pass"
        }

        with patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class:

            # Setup mocks
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # All attempts fail
            mock_riot_client.start_riot_client.side_effect = Exception("Always fails")

            # Execute and verify exception
            with pytest.raises(ProcessError, match="Failed to start Riot processes after 2 attempts"):
                await self.process_manager.start_safely(params, max_attempts=2)

            # Verify attempts
            assert mock_riot_client.start_riot_client.call_count == 2

    @pytest.mark.asyncio
    async def test_start_safely_locale_validation_failure(self):
        """로케일 검증 실패 테스트."""
        params = {
            "region": "na",
            "locale": "en_US",
            "username": "test_user",
            "password": "test_pass"
        }

        with patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class:

            # Setup mocks
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # Mock successful start but wrong locale
            mock_league_ux.get_state.return_value = {"action": "Idle"}
            mock_league_ux.get_region_locale.return_value = {"locale": "ko_KR"}  # Wrong locale

            # Execute and verify exception
            with pytest.raises(CustomError, match="Locale is not correct"):
                await self.process_manager.start_safely(params)

    @pytest.mark.asyncio
    async def test_start_safely_client_not_ready(self):
        """클라이언트가 준비되지 않은 상태 테스트."""
        params = {
            "region": "na",
            "locale": "en_US",
            "username": "test_user",
            "password": "test_pass"
        }

        with patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class:

            # Setup mocks
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # Mock successful start but client not ready
            mock_league_ux.get_state.return_value = {"action": "Busy"}  # Not Idle

            # Execute and verify exception
            with pytest.raises(ProcessError, match="Client is not ready"):
                await self.process_manager.start_safely(params, max_attempts=1)

    @pytest.mark.asyncio
    async def test_stop_windows_processes(self):
        """Windows 프로세스 중지 테스트."""
        self.platform_resolver.is_windows.return_value = True

        with patch('subprocess.run') as mock_subprocess, \
             patch('lol_replay_recorder.utils.utils.sleep_in_seconds') as mock_sleep:

            # Mock subprocess responses
            mock_subprocess.return_value.stdout = "INFO: No tasks are running"

            # Execute
            await self.process_manager.stop_windows_processes()

            # Verify taskkill commands were called
            expected_processes = [
                "RiotClientUx.exe",
                "RiotClientServices.exe",
                "RiotClient.exe",
                "Riot Client.exe",
                "LeagueClient.exe",
                "League of Legends.exe",
                "LeagueClientUxRender.exe"
            ]

            # Check that taskkill was called for each process
            kill_calls = [call for call in mock_subprocess.call_args_list
                         if 'taskkill' in str(call)]
            assert len(kill_calls) == len(expected_processes)

    @pytest.mark.asyncio
    async def test_stop_unix_processes(self):
        """Unix 프로세스 중지 테스트."""
        self.platform_resolver.is_windows.return_value = False

        with patch('subprocess.run') as mock_subprocess, \
             patch('os.kill') as mock_kill, \
             patch('lol_replay_recorder.utils.utils.sleep_in_seconds') as mock_sleep:

            # Mock pgrep finding processes
            mock_subprocess.side_effect = [
                # First pgrep call (find processes)
                MagicMock(returncode=0, stdout="1234\n5678"),
                # Second pgrep call (check if still running)
                MagicMock(returncode=1, stdout=""),
                # Same pattern for each process name
                MagicMock(returncode=0, stdout="9012"),
                MagicMock(returncode=1, stdout=""),
                MagicMock(returncode=0, stdout="3456"),
                MagicMock(returncode=1, stdout=""),
                MagicMock(returncode=0, stdout="7890"),
                MagicMock(returncode=1, stdout=""),
                MagicMock(returncode=0, stdout="2345"),
                MagicMock(returncode=1, stdout=""),
            ]

            # Execute
            await self.process_manager.stop_unix_processes()

            # Verify kill was called
            assert mock_kill.call_count == 6  # 6 PIDs found (1234, 5678, 9012, 3456, 7890, 2345)
            kill_calls = mock_kill.call_args_list
            assert kill_calls[0][0] == (1234, signal.SIGTERM)
            assert kill_calls[1][0] == (5678, signal.SIGTERM)

    @pytest.mark.asyncio
    async def test_stop_riot_processes_windows(self):
        """Windows에서 Riot 프로세스 중지 테스트."""
        self.platform_resolver.is_windows.return_value = True

        with patch.object(self.process_manager, 'stop_windows_processes') as mock_stop_windows, \
             patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class:

            # Setup mocks
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # Execute
            await self.process_manager.stop_riot_processes()

            # Verify
            mock_stop_windows.assert_called_once()
            mock_riot_client.remove_lockfile.assert_called_once()
            mock_league_ux.remove_lockfile.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_riot_processes_unix(self):
        """Unix에서 Riot 프로세스 중지 테스트."""
        self.platform_resolver.is_windows.return_value = False

        with patch.object(self.process_manager, 'stop_unix_processes') as mock_stop_unix, \
             patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class:

            # Setup mocks
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # Execute
            await self.process_manager.stop_riot_processes()

            # Verify
            mock_stop_unix.assert_called_once()
            mock_riot_client.remove_lockfile.assert_called_once()
            mock_league_ux.remove_lockfile.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_riot_processes_lockfile_errors_ignored(self):
        """Lockfile 제거 오류가 무시되는지 테스트."""
        self.platform_resolver.is_windows.return_value = True

        with patch.object(self.process_manager, 'stop_windows_processes'), \
             patch('lol_replay_recorder.controllers.riot_game_client.RiotGameClient') as mock_riot_client_class, \
             patch('lol_replay_recorder.controllers.league_client_ux.LeagueClientUx') as mock_league_ux_class:

            # Setup mocks to raise exceptions
            mock_riot_client = AsyncMock()
            mock_league_ux = AsyncMock()
            mock_riot_client.remove_lockfile.side_effect = Exception("Lockfile error")
            mock_league_ux.remove_lockfile.side_effect = Exception("Lockfile error")
            mock_riot_client_class.return_value = mock_riot_client
            mock_league_ux_class.return_value = mock_league_ux

            # Execute (should not raise exception)
            await self.process_manager.stop_riot_processes()

            # Verify methods were called despite errors
            mock_riot_client.remove_lockfile.assert_called_once()
            mock_league_ux.remove_lockfile.assert_called_once()

    def test_initialization_with_window_client(self):
        """Window 클라이언트로 초기화 테스트."""
        mock_window_client = MagicMock()
        process_manager = ProcessManager(self.platform_resolver, mock_window_client)

        assert process_manager.platform == self.platform_resolver
        assert process_manager.window_client == mock_window_client

    def test_initialization_without_window_client(self):
        """Window 클라이언트 없이 초기화 테스트."""
        process_manager = ProcessManager(self.platform_resolver)

        assert process_manager.platform == self.platform_resolver
        assert process_manager.window_client is None