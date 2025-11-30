import os
import platform
from typing import List, Optional
from pathlib import Path

from ...domain.errors import CustomError


class PlatformResolver:
    """
    플랫폼별 경로 및 설정 해결을 담당하는 클래스.

    League of Legends 설치 경로, lockfile 경로, 설정 파일 경로 등
    플랫폼(Windows, macOS, Linux)에 따라 다른 경로들을 관리합니다.
    """

    # 하드코딩된 설치 경로 상수
    WINDOWS_INSTALL_PATHS = [
        "C:\\Riot Games\\League of Legends",
        "D:\\Riot Games\\League of Legends",
        "C:\\Program Files\\Riot Games\\League of Legends",
        "C:\\Program Files (x86)\\Riot Games\\League of Legends",
    ]

    MACOS_INSTALL_PATHS = [
        "/Applications/League of Legends.app/Contents/LoL",
        os.path.expanduser("~/Applications/League of Legends.app/Contents/LoL"),
    ]

    LINUX_INSTALL_PATHS = [
        os.path.expanduser("~/.config/Riot Games/League of Legends"),
        "/opt/riot-games/league-of-legends",
        "/usr/local/share/league-of-legends",
    ]

    # Riot Client 경로
    RIOT_CLIENT_WINDOWS_PATHS = [
        "C:\\Riot Games\\Riot Client",
        "C:\\Program Files\\Riot Games\\Riot Client",
        "C:\\Program Files (x86)\\Riot Games\\Riot Client",
    ]

    # 설정 파일 경로
    WINDOWS_PRODUCT_SETTINGS_PATH = os.path.join(
        "C:", "ProgramData", "Riot Games", "Metadata",
        "league_of_legends.live", "league_of_legends.live.product_settings.yaml"
    )

    UNIX_PRODUCT_SETTINGS_PATH = os.path.expanduser(
        "~/.config/Riot Games/Metadata/league_of_legends.live/league_of_legends.live.product_settings.yaml"
    )

    def __init__(self) -> None:
        """PlatformResolver 초기화."""
        self.system = platform.system()

    def get_installed_paths(self) -> List[str]:
        """
        현재 플랫폼의 League of Legends 설치 경로들을 반환합니다.

        Returns:
            List[str]: 존재하는 설치 경로 목록
        """
        if self.system == "Windows":
            return self._find_windows_installed()
        elif self.system == "Darwin":  # macOS
            return [path for path in self.MACOS_INSTALL_PATHS if os.path.exists(path)]
        else:  # Linux
            return [path for path in self.LINUX_INSTALL_PATHS if os.path.exists(path)]

    def _find_windows_installed(self) -> List[str]:
        """
        Windows에서 League of Legends 설치 경로를 찾습니다.

        Returns:
            List[str]: 존재하는 설치 경로 목록
        """
        found_paths = []
        for path in self.WINDOWS_INSTALL_PATHS:
            if os.path.exists(path):
                found_paths.append(path)

        # 사용자별 Riot Games 경로도 확인
        user_riot_path = os.path.expanduser("~\\Riot Games\\League of Legends")
        if os.path.exists(user_riot_path) and user_riot_path not in found_paths:
            found_paths.append(user_riot_path)

        return found_paths

    def get_riot_client_lockfile_path(self) -> str:
        """
        Riot Client lockfile 경로를 반환합니다.

        Returns:
            str: Riot Client lockfile 경로

        Raises:
            CustomError: 경로를 찾을 수 없는 경우
        """
        if self.system == "Windows":
            local_app_data = os.environ.get('LOCALAPPDATA', '')
            if not local_app_data:
                raise CustomError("LOCALAPPDATA environment variable not found")
            return str(Path(local_app_data) / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile')
        else:
            # Unix 계열의 경우 Riot Client는 보통 Windows와 동일한 위치에
            return os.path.expanduser("~/.config/Riot Games/Riot Client/Config/lockfile")

    def get_league_client_lockfile_path(self) -> str:
        """
        League Client lockfile 경로를 반환합니다.

        Returns:
            str: League Client lockfile 경로
        """
        if self.system == "Windows":
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            return os.path.join(local_app_data, "Riot Games", "League of Legends", "lockfile")
        elif self.system == "Darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/Riot Games/League of Legends/lockfile")
        else:  # Linux
            return os.path.expanduser("~/.config/Riot Games/League of Legends/lockfile")

    def get_product_settings_path(self) -> str:
        """
        product_settings.yaml 파일 경로를 반환합니다.

        Returns:
            str: product_settings.yaml 파일 경로
        """
        if self.system == "Windows":
            return self.WINDOWS_PRODUCT_SETTINGS_PATH
        else:  # macOS/Linux
            return self.UNIX_PRODUCT_SETTINGS_PATH

    def get_config_file_path(self, install_path: str) -> Optional[str]:
        """
        설치 디렉토리 내에서 game.cfg 파일 경로를 찾습니다.

        Args:
            install_path: 기본 설치 경로

        Returns:
            Optional[str]: 설정 파일 경로 또는 None (찾지 못한 경우)
        """
        potential_config_paths = [
            os.path.join(install_path, "DATA", "CFG", "game.cfg"),
            os.path.join(install_path, "Config", "game.cfg"),
            os.path.join(install_path, "Game", "Config", "game.cfg")
        ]

        for config_path in potential_config_paths:
            if os.path.exists(config_path):
                return config_path

        return None

    def get_input_ini_path(self) -> str:
        """
        현재 플랫폼의 input.ini 파일 경로를 반환합니다.

        Returns:
            str: input.ini 파일 경로
        """
        if self.system == "Windows":
            # 설치 경로가 여러 개일 수 있으므로 첫 번째 경로 사용
            installed_paths = self.get_installed_paths()
            if installed_paths:
                return os.path.join(installed_paths[0], "Config", "input.ini")
            # 기본 경로 fallback
            return os.path.join("C:", "Riot Games", "League of Legends", "Config", "input.ini")
        elif self.system == "Darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/Riot Games/League of Legends/Config/input.ini")
        else:  # Linux
            return os.path.expanduser("~/.config/Riot Games/League of Legends/Config/input.ini")

    def get_riot_client_executable_path(self) -> str:
        """
        RiotClientServices.exe 실행 파일 경로를 반환합니다.

        Returns:
            str: RiotClientServices.exe 경로
        """
        if self.system == "Windows":
            # Windows 경로 중에서 RiotClientServices.exe가 있는 경로 찾기
            for path in self.RIOT_CLIENT_WINDOWS_PATHS:
                exe_path = os.path.join(path, "RiotClientServices.exe")
                if os.path.exists(exe_path):
                    return f'"{exe_path}"'

            # 기본 경로 fallback
            return '"C:\\Riot Games\\Riot Client\\RiotClientServices.exe"'
        else:
            # Unix 계열에서는 다른 실행 파일 사용
            return "riot-client"

    def is_windows(self) -> bool:
        """현재 플랫폼이 Windows인지 확인합니다."""
        return self.system == "Windows"

    def is_macos(self) -> bool:
        """현재 플랫폼이 macOS인지 확인합니다."""
        return self.system == "Darwin"

    def is_linux(self) -> bool:
        """현재 플랫폼이 Linux인지 확인합니다."""
        return self.system == "Linux"