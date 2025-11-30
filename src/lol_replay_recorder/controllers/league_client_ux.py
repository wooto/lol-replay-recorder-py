import asyncio
import os
import platform
from typing import Any, Dict, Optional

from ..models.summoner import Summoner
from ..domain.errors import CustomError
from ..clients.http.lcu import LCUClient
from ..services.process.platform import PlatformResolver
from ..utils.utils import sleep_in_seconds, refine_region
from ..constants import (
    PLATFORM_WINDOWS,
    PLATFORM_DARWIN,
    DEFAULT_WINDOWS_INSTALL_PATH,
    MAC_LEAGUE_CLIENT_PATH,
    MAC_USER_LEAGUE_CLIENT_PATH,
    DEFAULT_RETRY_COUNT,
)
# Import constants after path fix
try:
    from .constants import (
        LEAGUE_CLIENT_WINDOW_TITLE,
        LCUX_DEFAULT_RETRIES,
        LCUX_MAX_ATTEMPTS,
        LCUX_DEFAULT_RETRIES_REGION,
        LCUX_DEFAULT_RETRIES_HIGHLIGHTS,
        LCU_HIGHLIGHTS_FOLDER_PATH_ENDPOINT,
    )
except ImportError:
    # Fallback values if constants file has issues
    LEAGUE_CLIENT_WINDOW_TITLE = "League Client"
    LCUX_DEFAULT_RETRIES = 3
    LCUX_MAX_ATTEMPTS = 30
    LCUX_DEFAULT_RETRIES_REGION = 3
    LCUX_DEFAULT_RETRIES_HIGHLIGHTS = 3
    LCU_HIGHLIGHTS_FOLDER_PATH_ENDPOINT = "/lol-highlights/v1/highlights-folder-path"
from .window_handler import WindowHandler


class LeagueClientUx:
    """
    Controller for interacting with League Client UX API.

    Handles League Client automation including:
    - Client startup and state management
    - Game settings configuration
    - Replay management
    - Match history and summoner data
    - Window management and focus
    """

    def __init__(
        self,
        lockfile_path: Optional[str] = None,
        platform_resolver: Optional[PlatformResolver] = None
    ):
        """
        Initialize LeagueClientUx controller.

        Args:
            lockfile_path: Optional custom lockfile path for testing
            platform_resolver: Optional platform resolver for path management
        """
        self.platform_resolver = platform_resolver or PlatformResolver()
        self.patch: str = ""
        self.lockfile_path: str = lockfile_path or ""
        self.window_handler: WindowHandler = WindowHandler()
        self.lcu_client: Optional[LCUClient] = None

    async def __aenter__(self) -> "LeagueClientUx":
        """Async context manager entry."""
        if not self.lockfile_path:
            self.lockfile_path = await self.get_lockfile_path()
        self.lcu_client = LCUClient(self.lockfile_path)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        pass

    def _ensure_lcu_client(self) -> LCUClient:
        """Ensure LCU client is initialized."""
        if self.lcu_client is None:
            if not self.lockfile_path:
                raise CustomError("LCU client not initialized. Use async context manager or set lockfile_path first.")
            self.lcu_client = LCUClient(self.lockfile_path)
        return self.lcu_client

    async def _make_lcu_request(
        self,
        endpoint: str,
        method: str = "GET",
        body: Optional[Dict[str, Any]] = None,
        retries: int = DEFAULT_RETRY_COUNT,
    ) -> Any:
        """Make LCU request using the LCU client."""
        client = self._ensure_lcu_client()
        return await client.request(endpoint, method, body, retries)

    # CLIENT STARTUP AND MANAGEMENT //

    async def start_client(self, params: Dict[str, Any]) -> None:
        """
        Start the League Client with specified parameters.

        Args:
            params: Dictionary containing 'region' (PlatformId) and 'locale' (Locale)
        """
        system = platform.system()
        region = refine_region(params["region"]).upper()
        locale = params["locale"]

        if system == PLATFORM_WINDOWS:
            exe_path = DEFAULT_WINDOWS_INSTALL_PATH + "\\LeagueClient.exe"
            cmd_args = [
                exe_path,
                f"--region={region}",
                f"--locale={locale}",
            ]

            try:
                await asyncio.create_subprocess_exec(
                    *cmd_args,
                )

                # Wait for process to complete or let it run in background
                # await process.communicate()  # Uncomment if you want to wait for completion

            except Exception as e:
                print(f"Failed to start LeagueClient: {e}")
                raise

        elif system == "Darwin":  # macOS
            app_path = "/Applications/League of Legends.app/Contents/MacOS/LeagueClient"
            if not os.path.exists(app_path):
                # Try alternative path
                app_path = os.path.expanduser("~/Applications/League of Legends.app/Contents/MacOS/LeagueClient")

            if not os.path.exists(app_path):
                raise FileNotFoundError("League of Legends application not found")

            cmd_args = [
                app_path,
                f"--region={region}",
                f"--locale={locale}",
            ]

            try:
                await asyncio.create_subprocess_exec(*cmd_args)
                # await process.communicate()  # Uncomment if you want to wait for completion

            except Exception as e:
                print(f"Failed to start LeagueClient: {e}")
                raise
        else:
            raise NotImplementedError(f"Starting League Client not supported on {system}")

    async def wait_for_client_to_be_ready(self) -> bool:
        """
        Wait for League Client to be ready by checking state endpoint.

        Returns:
            True when client is ready

        Raises:
            CustomError: If client takes too long to start
        """
        max_attempts = 30

        for i in range(max_attempts):
            try:
                await self.get_state({"retry": 0})
                print("Client is ready.")
                return True
            except Exception:
                await sleep_in_seconds(1)

        raise CustomError("League Client took too long to start.")

    async def focus_client_window(self, window_title: str = "League of Legends") -> None:
        """
        Focus the League Client window.

        Args:
            window_title: Title of the window to focus
        """
        try:
            await self.window_handler.focus_client_window(window_title)
        except Exception as e:
            print(f"Failed to focus client window: {e}")

    # GAME SETTINGS AND CONFIGURATION //

    async def get_highlights_folder_path(self) -> str:
        """Get the highlights folder path from the client."""
        return await self._make_lcu_request("/lol-highlights/v1/highlights-folder-path", "GET", None, 3
        )

    async def get_game_settings(self) -> Dict[str, Any]:
        """Get current game settings."""
        return await self._make_lcu_request("/lol-game-settings/v1/game-settings"
        )

    async def get_input_settings(self) -> Dict[str, Any]:
        """Get current input settings."""
        return await self._make_lcu_request(
            "/lol-game-settings/v1/input-settings"
        )

    async def get_region_locale(self, retries: int = 3) -> Dict[str, Any]:
        """
        Get region and locale information.

        Args:
            retries: Number of retry attempts

        Returns:
            Dictionary containing region and locale data
        """
        return await self._make_lcu_request("/riotclient/region-locale", retries=retries
        )

    async def patch_game_settings(self, settings_resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Patch game settings with provided resource.

        Args:
            settings_resource: Settings to patch

        Returns:
            Updated settings response
        """
        return await self._make_lcu_request("/lol-game-settings/v1/game-settings", method="PATCH", body=settings_resource
        )

    async def save_game_settings(self) -> bool:
        """Save current game settings."""
        return await self._make_lcu_request(
            "/lol-game-settings/v1/save", method="POST"
        )

    async def disable_window_mode(self) -> Dict[str, Any]:
        """
        Disable windowed mode for game recording.

        Returns:
            Updated settings response

        Raises:
            CustomError: If settings cannot be saved
        """
        settings_resource = {
            "General": {
                "WindowMode": 0,
            },
        }

        updated_settings = await self.patch_game_settings(settings_resource)
        saved = await self.save_game_settings()

        if not saved:
            raise CustomError(
                "Failed to disable windowed mode automatically. Please manually disable it "
                "in the League Client settings before attempting to record a clip."
            )

        return updated_settings

    async def enable_window_mode(self) -> Dict[str, Any]:
        """
        Enable windowed mode.

        Returns:
            Updated settings response

        Raises:
            CustomError: If settings cannot be saved
        """
        settings_resource = {
            "General": {
                "WindowMode": 1,
            },
        }

        updated_settings = await self.patch_game_settings(settings_resource)
        saved = await self.save_game_settings()

        if not saved:
            raise CustomError(
                "Failed to enable windowed mode automatically. Please manually enable it "
                "in the League Client settings before attempting to record a clip."
            )

        return updated_settings

    # REPLAY MANAGEMENT //

    async def get_replay_config(self) -> Dict[str, Any]:
        """Get replay configuration."""
        return await self._make_lcu_request("/lol-replays/v1/configuration"
        )

    async def get_replay_metadata(self, match_id: str) -> Dict[str, Any]:
        """
        Get replay metadata for a specific match.

        Args:
            match_id: Match ID to get metadata for

        Returns:
            Replay metadata including download state
        """
        return await self._make_lcu_request(
            f"/lol-replays/v1/metadata/{match_id}"
        )

    async def get_rofls_path(self) -> str:
        """Get the ROFL (replay files) path."""
        return await self._make_lcu_request(
            "/lol-replays/v1/rofls/path"
        )

    async def download_replay(self, match_id: str) -> None:
        """
        Download a replay for a specific match.

        Args:
            match_id: Match ID to download replay for

        Raises:
            CustomError: If download fails
        """
        await self._make_lcu_request(
            f"/lol-replays/v1/rofls/{match_id}/download",
            method="POST",
            retries=10
        )

        await self.wait_for_replay_download_to_complete(match_id)

    async def wait_for_replay_download_to_complete(self, match_id: str) -> None:
        """
        Wait for replay download to complete.

        Args:
            match_id: Match ID being downloaded

        Raises:
            CustomError: If download fails or invalid state encountered
        """
        valid_download_states = ["checking", "downloading", "watch"]
        completed_state = "watch"

        while True:
            metadata = await self.get_replay_metadata(match_id)
            download_state = metadata.get("state")

            if download_state not in valid_download_states:
                raise CustomError(
                    f"Failed to download replay for matchId: {match_id}. "
                    f"Download state: {download_state}. The riot replay service may be down, "
                    "please try again later."
                )

            if download_state == completed_state:
                break

            await sleep_in_seconds(2)

    async def launch_replay(self, match_id: str) -> None:
        """
        Launch replay viewer for a specific match.

        Args:
            match_id: Match ID to launch replay for
        """
        await self.download_replay(match_id)

        await self._make_lcu_request(
            f"/lol-replays/v1/rofls/{match_id}/watch",
            method="POST",
            retries=10
        )

    # MATCH HISTORY AND DATA //

    async def get_end_of_match_data_by_match_id(self, match_id: str) -> Dict[str, Any]:
        """
        Get end of match data for a specific match.

        Args:
            match_id: Match ID to get data for

        Returns:
            End of match data
        """
        return await self._make_lcu_request(
            f"/lol-match-history/v1/games/{match_id}"
        )

    async def get_summoners_by_riot_id(self, riot_id: str) -> Dict[str, Any]:
        """
        Get summoner data by Riot ID.

        Args:
            riot_id: Riot ID (e.g., "Player#1234")

        Returns:
            Summoner data
        """
        return await self._make_lcu_request(
            f"/lol-summoner/v1/summoners?name={riot_id}"
        )

    async def get_match_history_by_puuid(self, puuid: str, beg_index: int, end_index: int) -> list[Any]:
        """
        Get match history for a summoner by PUUID.

        Args:
            puuid: Player UUID
            beg_index: Beginning index
            end_index: Ending index

        Returns:
            List of match history games
        """
        match_data = await self._make_lcu_request(
            f"/lol-match-history/v1/products/lol/{puuid}/matches?begIndex={beg_index}&endIndex={end_index}"
        )
        return match_data.get("games", {}).get("games", [])

    async def get_match_timeline_by_match_id(self, match_id: str) -> list[Any]:
        """
        Get match timeline data for a specific match.

        Args:
            match_id: Match ID to get timeline for

        Returns:
            List of timeline frames
        """
        match_data = await self._make_lcu_request(
            f"/lol-match-history/v1/game-timelines/{match_id}"
        )
        return match_data.get("frames", [])

    # CLIENT STATE AND SYSTEM //

    async def get_patch_version(self) -> str:
        """
        Get current patch version.

        Returns:
            Current patch version string
        """
        if self.patch:
            return self.patch

        raw_patch_data = await self._make_lcu_request("/lol-patch/v1/game-version"
        )

        self.patch = raw_patch_data
        return raw_patch_data

    async def get_state(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get current client state.

        Args:
            options: Optional parameters including retry count

        Returns:
            Client state data
        """
        if options is None:
            options = {}

        retry = options.get("retry", 0)

        return await self._make_lcu_request("/lol-patch/v1/products/league_of_legends/state", "GET", None, retry
        )

    async def get_queues(self) -> list[Any]:
        """Get available game queues."""
        return await self._make_lcu_request(
            "lol-game-queues/v1/queues"
        )

    async def get_current_summoner(self) -> Summoner:
        """
        Get current logged-in summoner.

        Returns:
            Summoner object with current user data
        """
        current_summoner = await self._make_lcu_request(
            "/lol-summoner/v1/current-summoner")

        return Summoner(
            summoner_name=current_summoner.get("displayName", ""),
            tagline=current_summoner.get("tagLine", ""),
            puuid=current_summoner.get("puuid", "")
        )

    # LOCKFILE MANAGEMENT //

    async def get_lockfile_path(self) -> str:
        """
        Get the path to the League Client lockfile.

        Returns:
            Path to lockfile based on operating system
        """
        return self.platform_resolver.get_league_client_lockfile_path()

    async def remove_lockfile(self) -> None:
        """Remove the League Client lockfile. Ignores errors if file doesn't exist."""
        try:
            if os.path.exists(self.lockfile_path):
                os.remove(self.lockfile_path)
        except Exception:
            # Silently ignore errors (file might not exist or be in use)
            pass