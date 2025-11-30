import os
import platform
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from lol_replay_recorder.services.process.platform import PlatformResolver
from lol_replay_recorder.domain.errors import CustomError


class TestPlatformResolver:
    """PlatformResolver 클래스에 대한 단위 테스트."""

    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.resolver = PlatformResolver()

    def test_init(self):
        """PlatformResolver 초기화 테스트."""
        assert self.resolver.system == platform.system()

    def test_is_windows(self):
        """Windows 플랫폼 확인 테스트."""
        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()
            assert resolver.is_windows() is True
            assert resolver.is_macos() is False
            assert resolver.is_linux() is False

    def test_is_macos(self):
        """macOS 플랫폼 확인 테스트."""
        with patch('platform.system', return_value="Darwin"):
            resolver = PlatformResolver()
            assert resolver.is_windows() is False
            assert resolver.is_macos() is True
            assert resolver.is_linux() is False

    def test_is_linux(self):
        """Linux 플랫폼 확인 테스트."""
        with patch('platform.system', return_value="Linux"):
            resolver = PlatformResolver()
            assert resolver.is_windows() is False
            assert resolver.is_macos() is False
            assert resolver.is_linux() is True

    @patch('os.path.exists')
    def test_get_installed_paths_windows(self, mock_exists):
        """Windows 설치 경로 확인 테스트."""
        mock_exists.return_value = True

        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()
            paths = resolver.get_installed_paths()

            # 윈도우 기본 경로들이 포함되어야 함
            assert "C:\\Riot Games\\League of Legends" in paths
            assert "D:\\Riot Games\\League of Legends" in paths

    @patch('os.path.exists')
    def test_get_installed_paths_macos(self, mock_exists):
        """macOS 설치 경로 확인 테스트."""
        mock_exists.return_value = True

        with patch('platform.system', return_value="Darwin"):
            resolver = PlatformResolver()
            paths = resolver.get_installed_paths()

            # macOS 기본 경로들이 포함되어야 함
            assert "/Applications/League of Legends.app/Contents/LoL" in paths
            assert any("Applications" in path for path in paths)

    @patch('os.path.exists')
    def test_get_installed_paths_linux(self, mock_exists):
        """Linux 설치 경로 확인 테스트."""
        mock_exists.return_value = True

        with patch('platform.system', return_value="Linux"):
            resolver = PlatformResolver()
            paths = resolver.get_installed_paths()

            # Linux 기본 경로들이 포함되어야 함
            assert any(".config/Riot Games" in path for path in paths)

    @patch('os.path.exists')
    def test_get_installed_paths_no_existing(self, mock_exists):
        """존재하지 않는 설치 경로 테스트."""
        mock_exists.return_value = False

        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()
            paths = resolver.get_installed_paths()

            # 존재하지 않는 경로는 제외되어야 함
            assert len(paths) == 0

    def test_get_riot_client_lockfile_path_windows(self):
        """Windows Riot Client lockfile 경로 테스트."""
        test_localappdata = "C:\\Users\\Test\\AppData\\Local"

        with patch('platform.system', return_value="Windows"):
            with patch.dict(os.environ, {'LOCALAPPDATA': test_localappdata}):
                resolver = PlatformResolver()
                path = resolver.get_riot_client_lockfile_path()

                expected = os.path.join(test_localappdata, "Riot Games", "Riot Client", "Config", "lockfile")
                assert path == expected

    def test_get_riot_client_lockfile_path_windows_no_env(self):
        """Windows에서 LOCALAPPDATA 환경변수가 없을 경우 테스트."""
        with patch('platform.system', return_value="Windows"):
            with patch.dict(os.environ, {}, clear=True):
                resolver = PlatformResolver()

                with pytest.raises(CustomError, match="LOCALAPPDATA environment variable not found"):
                    resolver.get_riot_client_lockfile_path()

    def test_get_riot_client_lockfile_path_unix(self):
        """Unix 계열 Riot Client lockfile 경로 테스트."""
        with patch('platform.system', return_value="Darwin"):
            resolver = PlatformResolver()
            path = resolver.get_riot_client_lockfile_path()

            expected = os.path.expanduser("~/.config/Riot Games/Riot Client/Config/lockfile")
            assert path == expected

    def test_get_league_client_lockfile_path_windows(self):
        """Windows League Client lockfile 경로 테스트."""
        test_localappdata = "C:\\Users\\Test\\AppData\\Local"

        with patch('platform.system', return_value="Windows"):
            with patch.dict(os.environ, {'LOCALAPPDATA': test_localappdata}):
                resolver = PlatformResolver()
                path = resolver.get_league_client_lockfile_path()

                expected = os.path.join(test_localappdata, "Riot Games", "League of Legends", "lockfile")
                assert path == expected

    def test_get_league_client_lockfile_path_macos(self):
        """macOS League Client lockfile 경로 테스트."""
        with patch('platform.system', return_value="Darwin"):
            resolver = PlatformResolver()
            path = resolver.get_league_client_lockfile_path()

            expected = os.path.expanduser("~/Library/Application Support/Riot Games/League of Legends/lockfile")
            assert path == expected

    def test_get_league_client_lockfile_path_linux(self):
        """Linux League Client lockfile 경로 테스트."""
        with patch('platform.system', return_value="Linux"):
            resolver = PlatformResolver()
            path = resolver.get_league_client_lockfile_path()

            expected = os.path.expanduser("~/.config/Riot Games/League of Legends/lockfile")
            assert path == expected

    def test_get_product_settings_path_windows(self):
        """Windows product_settings.yaml 경로 테스트."""
        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()
            path = resolver.get_product_settings_path()

            expected = os.path.join(
                "C:", "ProgramData", "Riot Games", "Metadata",
                "league_of_legends.live", "league_of_legends.live.product_settings.yaml"
            )
            assert path == expected

    def test_get_product_settings_path_unix(self):
        """Unix 계열 product_settings.yaml 경로 테스트."""
        with patch('platform.system', return_value="Darwin"):
            resolver = PlatformResolver()
            path = resolver.get_product_settings_path()

            expected = os.path.expanduser(
                "~/.config/Riot Games/Metadata/league_of_legends.live/league_of_legends.live.product_settings.yaml"
            )
            assert path == expected

    @patch('os.path.exists')
    def test_get_config_file_path_found(self, mock_exists):
        """설정 파일 경로 찾기 테스트 (성공)."""
        mock_exists.side_effect = lambda path: "DATA/CFG/game.cfg" in path

        resolver = PlatformResolver()
        test_install_path = "/path/to/lol"
        config_path = resolver.get_config_file_path(test_install_path)

        assert config_path == os.path.join(test_install_path, "DATA", "CFG", "game.cfg")

    @patch('os.path.exists')
    def test_get_config_file_path_not_found(self, mock_exists):
        """설정 파일 경로 찾기 테스트 (실패)."""
        mock_exists.return_value = False

        resolver = PlatformResolver()
        test_install_path = "/path/to/lol"
        config_path = resolver.get_config_file_path(test_install_path)

        assert config_path is None

    def test_get_input_ini_path_windows(self):
        """Windows input.ini 경로 테스트."""
        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()

            # get_installed_paths가 빈 리스트를 반환하도록 mock
            with patch.object(resolver, 'get_installed_paths', return_value=[]):
                path = resolver.get_input_ini_path()

                # 기본 fallback 경로
                expected = os.path.join("C:", "Riot Games", "League of Legends", "Config", "input.ini")
                assert path == expected

    def test_get_input_ini_path_windows_with_installation(self):
        """Windows input.ini 경로 테스트 (설치 경로 있음)."""
        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()
            test_install_path = "D:\\Games\\League of Legends"

            with patch.object(resolver, 'get_installed_paths', return_value=[test_install_path]):
                path = resolver.get_input_ini_path()

                expected = os.path.join(test_install_path, "Config", "input.ini")
                assert path == expected

    def test_get_input_ini_path_macos(self):
        """macOS input.ini 경로 테스트."""
        with patch('platform.system', return_value="Darwin"):
            resolver = PlatformResolver()
            path = resolver.get_input_ini_path()

            expected = os.path.expanduser("~/Library/Application Support/Riot Games/League of Legends/Config/input.ini")
            assert path == expected

    def test_get_input_ini_path_linux(self):
        """Linux input.ini 경로 테스트."""
        with patch('platform.system', return_value="Linux"):
            resolver = PlatformResolver()
            path = resolver.get_input_ini_path()

            expected = os.path.expanduser("~/.config/Riot Games/League of Legends/Config/input.ini")
            assert path == expected

    def test_get_riot_client_executable_path_windows(self):
        """Windows RiotClientServices.exe 경로 테스트."""
        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()

            # 기본 경로 반환
            path = resolver.get_riot_client_executable_path()
            assert '"C:\\Riot Games\\Riot Client\\RiotClientServices.exe"' in path

    @patch('os.path.exists')
    def test_get_riot_client_executable_path_windows_found(self, mock_exists):
        """Windows에서 실제 실행 파일을 찾은 경우 테스트."""
        mock_exists.return_value = True

        with patch('platform.system', return_value="Windows"):
            resolver = PlatformResolver()
            path = resolver.get_riot_client_executable_path()

            # 실제 경로를 찾았다면 해당 경로 사용
            assert path.startswith('"')
            assert path.endswith('"')
            assert "RiotClientServices.exe" in path

    def test_get_riot_client_executable_path_unix(self):
        """Unix 계열 Riot Client 실행 파일 경로 테스트."""
        with patch('platform.system', return_value="Darwin"):
            resolver = PlatformResolver()
            path = resolver.get_riot_client_executable_path()

            assert path == "riot-client"

    def test_windows_install_paths_constants(self):
        """Windows 설치 경로 상수 테스트."""
        expected_paths = [
            "C:\\Riot Games\\League of Legends",
            "D:\\Riot Games\\League of Legends",
            "C:\\Program Files\\Riot Games\\League of Legends",
            "C:\\Program Files (x86)\\Riot Games\\League of Legends",
        ]
        assert PlatformResolver.WINDOWS_INSTALL_PATHS == expected_paths

    def test_macos_install_paths_constants(self):
        """macOS 설치 경로 상수 테스트."""
        expected_paths = [
            "/Applications/League of Legends.app/Contents/LoL",
            os.path.expanduser("~/Applications/League of Legends.app/Contents/LoL"),
        ]
        assert PlatformResolver.MACOS_INSTALL_PATHS == expected_paths

    def test_linux_install_paths_constants(self):
        """Linux 설치 경로 상수 테스트."""
        expected_paths = [
            os.path.expanduser("~/.config/Riot Games/League of Legends"),
            "/opt/riot-games/league-of-legends",
            "/usr/local/share/league-of-legends",
        ]
        assert PlatformResolver.LINUX_INSTALL_PATHS == expected_paths