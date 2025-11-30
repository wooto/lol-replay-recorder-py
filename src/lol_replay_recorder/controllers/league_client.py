import os
import platform
from typing import Any, Dict, Optional, List

from ..services.config.game_settings import GameSettingsManager
from ..services.config.editors.ini import IniEditor
from ..services.process.platform import PlatformResolver
from ..services.process.manager import ProcessManager
from ..utils.utils import sleep_in_seconds
from ..domain.errors import CustomError, ProcessError
from .riot_game_client import RiotGameClient
from .league_client_ux import LeagueClientUx
from .league_replay_client import LeagueReplayClient
from .window_handler import WindowHandler


class LeagueClient:
    """
    Main orchestrator for League of Legends client automation.

    Coordinates between LeagueClientUx, RiotGameClient, and LeagueReplayClient
    to provide high-level API for common operations including:
    - Client lifecycle management (start/stop processes)
    - Configuration management (locales, game settings)
    - Multi-platform support (Windows, macOS)
    - Complex workflows spanning multiple controllers
    """

    def __init__(self, platform_resolver: Optional[PlatformResolver] = None, process_manager: Optional[ProcessManager] = None) -> None:
        """Initialize LeagueClient orchestrator."""
        self.platform_resolver = platform_resolver or PlatformResolver()
        self._process_manager = process_manager or ProcessManager(self.platform_resolver)
        self._game_settings_manager: Optional[GameSettingsManager] = None
        self.riot_game_client: Optional[RiotGameClient] = None
        self.league_client_ux: Optional[LeagueClientUx] = None
        self.league_replay_client: Optional[LeagueReplayClient] = None
        self._window_handler: Optional[WindowHandler] = None

    # LAZY INITIALIZATION //

    def get_riot_game_client(self) -> RiotGameClient:
        """Get or create RiotGameClient instance."""
        if self.riot_game_client is None:
            self.riot_game_client = RiotGameClient()
        return self.riot_game_client

    def get_league_client_ux(self) -> LeagueClientUx:
        """Get or create LeagueClientUx instance."""
        if self.league_client_ux is None:
            self.league_client_ux = LeagueClientUx()
        return self.league_client_ux

    def get_league_replay_client(self) -> LeagueReplayClient:
        """Get or create LeagueReplayClient instance."""
        if self.league_replay_client is None:
            self.league_replay_client = LeagueReplayClient()
        return self.league_replay_client

    def _get_game_settings_manager(self) -> GameSettingsManager:
        """Get or create GameSettingsManager instance."""
        if self._game_settings_manager is None:
            self._game_settings_manager = GameSettingsManager(self.platform_resolver)
        return self._game_settings_manager

    def _get_window_handler(self) -> WindowHandler:
        """Get or create WindowHandler instance."""
        if self._window_handler is None:
            self._window_handler = WindowHandler()
        return self._window_handler

    # PROCESS MANAGEMENT //

    async def start_riot_processes_safely(self, params: Dict[str, Any]) -> None:
        """
        Safely start Riot processes with retry logic and validation.

        Args:
            params: Dictionary containing 'region' (Region), 'locale' (Locale),
                   'username' (str), and 'password' (str)

        Raises:
            CustomError: If processes fail to start or locale validation fails
        """
        # Set locale first (before starting processes)
        await self.set_locale(params["locale"])

        # Delegate to ProcessManager for process management
        await self._process_manager.start_safely(params)

    async def stop_riot_processes(self) -> None:
        """Stop all Riot-related processes and clean up lockfiles."""
        # Delegate to ProcessManager
        await self._process_manager.stop_riot_processes()

    # PATH AND INSTALLATION MANAGEMENT //

    def get_installed_paths(self) -> List[str]:
        """
        Get all League of Legends installation paths for current platform.

        Returns:
            List of installation paths
        """
        return self.platform_resolver.get_installed_paths()

    def get_product_settings_path(self) -> str:
        """
        Get the product settings YAML file path.

        Returns:
            Path to product_settings.yaml
        """
        return self.platform_resolver.get_product_settings_path()

    def get_config_file_paths(self) -> List[str]:
        """
        Get all game.cfg file paths from installed locations.

        Returns:
            List of config file paths
        """
        installed_paths = self.get_installed_paths()
        config_paths = []

        for install_path in installed_paths:
            config_path = self.get_config_file_path(install_path)
            if config_path:
                config_paths.append(config_path)

        return config_paths

    def get_config_file_path(self, initial_path: str) -> Optional[str]:
        """
        Find game.cfg path within an installation directory.

        Args:
            initial_path: Base installation path

        Returns:
            Config file path or None if not found
        """
        return self.platform_resolver.get_config_file_path(initial_path)

    # GAME CONFIGURATION //

    async def is_game_enabled(self, path: str) -> bool:
        """
        Check if replay API is enabled in game configuration.

        Args:
            path: Path to game.cfg file

        Returns:
            True if replay API is enabled, False otherwise
        """
        try:
            editor = IniEditor(path)
            enable_replay_api = editor.data.get("config", {}).get("General", {}).get("EnableReplayApi")
            return enable_replay_api in (1, True, "1")
        except Exception:
            return False

    async def set_game_enabled(self, path: str, enabled: bool) -> None:
        """
        Enable or disable replay API in game configuration.

        Args:
            path: Path to game.cfg file
            enabled: Whether to enable replay API
        """
        try:
            editor = IniEditor(path)
            editor.update_section("General", "EnableReplayApi", enabled)
            editor.save()
        except Exception as e:
            print(f"Error writing config file: {e}")

    def get_game_input_ini_path(self) -> str:
        """
        Get the input.ini file path for the current platform.

        Returns:
            Path to input.ini file
        """
        return self.platform_resolver.get_input_ini_path()

    async def set_default_input_ini(self) -> None:
        """Set default key bindings for player selection in input.ini."""
        try:
            input_path = self.get_game_input_ini_path()
            editor = IniEditor(input_path)

            # Set player selection key bindings
            player_keys = [
                ("GameEvents", "evtSelectOrderPlayer1", "[1]"),
                ("GameEvents", "evtSelectOrderPlayer2", "[2]"),
                ("GameEvents", "evtSelectOrderPlayer3", "[3]"),
                ("GameEvents", "evtSelectOrderPlayer4", "[4]"),
                ("GameEvents", "evtSelectOrderPlayer5", "[5]"),
            ]

            for section, key, value in player_keys:
                editor.update_section(section, key, value)

            editor.save()
        except Exception as e:
            print(f"Error writing input.ini file: {e}")

    async def set_locale(self, locale: str) -> None:
        """
        Set the default locale for the League Client.

        Args:
            locale: Locale string (e.g., 'en_US', 'ko_KR')

        Raises:
            CustomError: If locale is invalid
        """
        from ..models.locale import Locale
        game_settings = self._get_game_settings_manager()
        await game_settings.set_locale(Locale(locale))

    async def update_game_config(
        self,
        updates: dict[str, Any]
    ) -> None:
        """
        Update game configuration with provided updates.

        Args:
            updates: Dictionary of configuration updates
        """
        game_settings = self._get_game_settings_manager()
        await game_settings.update_game_config(updates)

    async def set_window_mode(
        self,
        enable: bool
    ) -> None:
        """
        Enable or disable window mode.

        Args:
            enable: Whether to enable window mode
        """
        game_settings = self._get_game_settings_manager()
        await game_settings.set_window_mode(enable)

    # WINDOW MANAGEMENT //

    async def focus_client_window(self) -> None:
        """Focus the League of Legends game window."""
        handler = self._get_window_handler()

        if self.platform_resolver.is_windows():
            target_title = "League of Legends (TM)"
        else:
            target_title = "League of Legends"

        await handler.focus_client_window(target_title)