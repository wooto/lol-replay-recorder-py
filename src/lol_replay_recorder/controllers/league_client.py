import os
import platform
import subprocess
import signal
from typing import Any, Dict, Optional, List

from ..services.config.editors.yaml import YamlEditor
from ..services.config.editors.ini import IniEditor
from ..services.process.platform import PlatformResolver
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

    def __init__(self, platform_resolver: Optional[PlatformResolver] = None) -> None:
        """Initialize LeagueClient orchestrator."""
        self.platform_resolver = platform_resolver or PlatformResolver()
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
        await self.stop_riot_processes()
        await self.set_locale(params["locale"])

        riot_client = self.get_riot_game_client()
        league_ux = self.get_league_client_ux()

        for attempt in range(5):
            try:
                await riot_client.start_riot_client(params["region"], params["locale"])
                await riot_client.login(params["username"], params["password"], params["region"])

                # Wait for client to be ready
                await league_ux.wait_for_client_to_be_ready()

                # Verify client is in idle state
                state = await league_ux.get_state({"retry": 1})
                if state.get("action") != "Idle":
                    raise ProcessError(f"Client is not ready: {state.get('action')}")

                break

            except Exception as e:
                print(f"Error starting Riot processes (attempt {attempt + 1}): {e}")
                if attempt < 4:  # Don't sleep on last attempt
                    await sleep_in_seconds(1)
                await self.stop_riot_processes()

                if attempt == 4:
                    raise CustomError(f"Failed to start Riot processes after 5 attempts: {e}")

        # Validate locale was set correctly
        region_locale = await league_ux.get_region_locale(30)
        if region_locale["locale"] != params["locale"]:
            raise CustomError(
                f"Locale is not correct: expected {params['locale']}, got {region_locale['locale']}"
            )

        await sleep_in_seconds(5)

    async def stop_riot_processes(self) -> None:
        """Stop all Riot-related processes and clean up lockfiles."""
        if self.platform_resolver.is_windows():
            await self._stop_windows_processes()
        else:
            await self._stop_unix_processes()

        # Clean up lockfiles
        riot_client = self.get_riot_game_client()
        league_ux = self.get_league_client_ux()

        try:
            await riot_client.remove_lockfile()
        except Exception:
            pass  # Ignore lockfile removal errors

        try:
            await league_ux.remove_lockfile()
        except Exception:
            pass  # Ignore lockfile removal errors

    async def _stop_windows_processes(self) -> None:
        """Stop Riot processes on Windows."""
        processes = [
            "RiotClientUx.exe",
            "RiotClientServices.exe",
            "RiotClient.exe",
            "Riot Client.exe",
            "LeagueClient.exe",
            "League of Legends.exe",
            "LeagueClientUxRender.exe"
        ]

        # Kill processes
        for process in processes:
            try:
                subprocess.run(
                    f"taskkill /F /IM \"{process}\" /T",
                    shell=True,
                    capture_output=True
                )
            except Exception:
                pass  # Ignore process kill errors

        # Wait for processes to fully terminate
        for process in processes:
            for _ in range(30):
                try:
                    result = subprocess.run(
                        f"tasklist /FI \"IMAGENAME eq {process}\"",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if process not in result.stdout:
                        break
                    await sleep_in_seconds(1)
                except Exception:
                    break

    async def _stop_unix_processes(self) -> None:
        """Stop Riot processes on Unix systems (macOS/Linux)."""
        process_names = [
            "LeagueClientUx",
            "RiotClientServices",
            "RiotClient",
            "LeagueClient",
            "League of Legends",
        ]

        for process_name in process_names:
            try:
                # Find and kill processes
                result = subprocess.run(
                    ["pgrep", "-f", process_name],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            try:
                                os.kill(int(pid.strip()), signal.SIGTERM)
                            except (ValueError, ProcessLookupError):
                                pass

            except Exception:
                pass  # Ignore errors

            # Wait for process to terminate
            for _ in range(10):
                try:
                    result = subprocess.run(
                        ["pgrep", "-f", process_name],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        break
                    await sleep_in_seconds(1)
                except Exception:
                    break

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
            input_path = await self.get_game_input_ini_path()
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
        try:
            yaml_path = self.get_product_settings_path()
            yaml_editor = YamlEditor(yaml_path)

            available_locales = yaml_editor.data.get("locale_data", {}).get("available_locales", [])
            if locale not in available_locales:
                raise CustomError(
                    f"Invalid locale: {locale}, available locales: {available_locales}"
                )

            yaml_editor.update("locale_data.default_locale", locale)
            yaml_editor.update("settings.locale", locale)
            yaml_editor.save_changes()

        except Exception as e:
            if isinstance(e, CustomError):
                raise
            print(f"Error setting locale: {e}")

    # WINDOW MANAGEMENT //

    async def focus_client_window(self) -> None:
        """Focus the League of Legends game window."""
        handler = self._get_window_handler()

        if self.platform_resolver.is_windows():
            target_title = "League of Legends (TM)"
        else:
            target_title = "League of Legends"

        await handler.focus_client_window(target_title)