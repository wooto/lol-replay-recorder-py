import os
from typing import Any
from ..models.riot_request import make_request
from ..models.replay_type import RecordingProperties, RenderProperties, GameData
from ..models.custom_error import CustomError
from ..utils.utils import sleep_in_seconds
from .window_handler import WindowHandler, Key

# Disable SSL warnings for self-signed certs
os.environ["PYTHONHTTPSVERIFY"] = "0"


class LeagueReplayClient:
    """Client for interacting with League of Legends Replay API."""

    def __init__(self) -> None:
        self.url = "https://127.0.0.1:2999"
        self.pid: int | None = None

    async def init(self) -> None:
        """Initialize client by fetching process ID."""
        try:
            pid = await self.get_process_id()
            self.set_process_id(pid)
        except Exception as e:
            print(f"Error initializing replay client: {e}")

    def set_process_id(self, pid: int) -> None:
        """Set the replay process ID."""
        self.pid = pid

    async def get_process_id(self) -> int:
        """Get the replay process ID from the API."""
        if self.pid:
            return self.pid

        replay_data = await make_request("GET", f"{self.url}/replay/game")
        if replay_data and "processID" in replay_data:
            self.pid = replay_data["processID"]

        if self.pid is None:
            raise RuntimeError("Could not get replay process ID")
        return self.pid

    async def exit(self) -> None:
        """Exit the replay by killing the process."""
        try:
            pid = await self.get_process_id()
            os.kill(pid, 9)  # SIGKILL
        except Exception:
            pass  # Silently ignore errors

    async def get_playback_properties(self) -> dict[str, Any]:
        """Get current playback properties."""
        return await make_request("GET", f"{self.url}/replay/playback")

    async def post_playback_properties(self, options: dict[str, Any]) -> dict[str, Any]:
        """Update playback properties."""
        return await make_request("POST", f"{self.url}/replay/playback", body=options)

    async def get_recording_properties(self) -> RecordingProperties:
        """Get current recording properties."""
        return await make_request("GET", f"{self.url}/replay/recording")

    async def post_recording_properties(self, options: dict[str, Any]) -> dict[str, Any]:
        """Update recording properties."""
        return await make_request("POST", f"{self.url}/replay/recording", body=options)

    async def get_render_properties(self) -> RenderProperties:
        """Get current render properties."""
        return await make_request("GET", f"{self.url}/replay/render")

    async def post_render_properties(self, options: dict[str, Any]) -> dict[str, Any]:
        """Update render properties."""
        return await make_request("POST", f"{self.url}/replay/render", body=options)

    async def load(self, timeout: int, num_retries: int) -> None:
        """Load replay and wait for it to be ready."""
        response_received = False

        while not response_received and num_retries > 0:
            try:
                await self.get_playback_properties()
                await self.get_recording_properties()
                response_received = True
            except Exception:
                num_retries -= 1
                print(
                    f"Couldn't connect to replay API, waiting {timeout} seconds "
                    f"then retrying ({num_retries} retries remaining)."
                )
                await sleep_in_seconds(timeout)

        if num_retries <= 0:
            raise CustomError(
                "Failed to launch replay. Please ensure the replay API is enabled "
                "and the client is running, then try again"
            )

        await self.wait_for_assets_to_load()

    async def wait_for_assets_to_load(self) -> None:
        """Wait for replay assets to load (time >= 15 or paused)."""
        while True:
            playback_state = await self.get_playback_properties()
            time = playback_state.get("time", 0)
            paused = playback_state.get("paused", False)

            if time >= 15 or paused:
                break

    async def wait_for_recording_to_finish(self, time: int) -> None:
        """Wait for recording to finish."""
        wait_time = time

        while True:
            await sleep_in_seconds(wait_time)
            recording_state = await self.get_recording_properties()
            recording = recording_state.get("recording", False)
            current_time = recording_state.get("currentTime", 0)
            end_time = recording_state.get("endTime", 0)
            wait_time = end_time - current_time  # type: ignore[operator]

            if not recording or wait_time <= 0:
                break

    async def get_all_game_data(self) -> GameData:
        """Get all game data."""
        return await make_request("GET", f"{self.url}/liveclientdata/allgamedata")

    async def get_in_game_position_by_summoner_name(self, summoner_name: str) -> int:
        """Get player position index by summoner name (0-9)."""
        data = await self.get_all_game_data()
        all_players = data.get("allPlayers", [])

        # all_players is assumed to be iterable from API response
        order_team = [p for p in all_players if isinstance(p, dict) and p.get("team") == "ORDER"]  # type: ignore[attr-defined]
        chaos_team = [p for p in all_players if isinstance(p, dict) and p.get("team") == "CHAOS"]  # type: ignore[attr-defined]

        # Check ORDER team
        for i, player in enumerate(order_team):
            if player.get("riotIdGameName") == summoner_name:
                return i

        # Check CHAOS team
        for i, player in enumerate(chaos_team):
            if player.get("riotIdGameName") == summoner_name:
                return i + 5

        raise CustomError("Summoner not found in game")

    async def focus_by_summoner_name(self, target_summoner_name: str) -> None:
        """Focus camera on a summoner by name."""
        position = await self.get_in_game_position_by_summoner_name(target_summoner_name)

        # Map position to keyboard key
        keys = [
            Key.Num1, Key.Num2, Key.Num3, Key.Num4, Key.Num5,
            Key.Q, Key.W, Key.E, Key.R, Key.T,
        ]
        keyboard_key = keys[position]

        handler = WindowHandler()

        for i in range(10):
            # Focus League of Legends window
            await handler.focus_client_window("League of Legends")

            # Press key 50 times
            for j in range(50):
                await handler.keyboard_type(keyboard_key)
                await sleep_in_seconds(0.2)

            await sleep_in_seconds(10)

            # Verify selection
            render_props = await self.get_render_properties()
            selection_name = render_props.get("selectionName", "")

            if selection_name == target_summoner_name:
                break