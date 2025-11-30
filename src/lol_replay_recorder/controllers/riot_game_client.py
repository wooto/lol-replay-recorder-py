import asyncio
import os
from base64 import b64encode
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional

from ..models.locale import Locale
from ..models.riot_request import make_request
from ..models.riot_types import Region
from ..utils.utils import refine_region, sleep_in_seconds
from ..domain.errors import ConfigError
from .window_handler import Key, WindowHandler


class LockfileCredentials(NamedTuple):
    """Lockfile credentials."""
    port: str
    password: str


class RegionLocale(NamedTuple):
    """Region and locale information."""
    locale: str
    region: str


class RiotGameClient:
    """Controller for interacting with Riot Game Client."""

    def __init__(self) -> None:
        self.riot_client_services_path = '"C:\\Riot Games\\Riot Client\\RiotClientServices.exe"'
        self.default_client_paths = ['C:\\Riot Games\\Riot Client']
        self._window_handler: Optional[WindowHandler] = None

    async def is_running(self) -> Dict[str, Any]:
        """Check if the Riot Game Client is running."""
        return await self._invoke_riot_request(
            await self.get_lockfile_path(),
            '/lol-patch/v1/products/league_of_legends/state',
            'GET',
            None,
            0,
        )

    async def login(self, username: str, password: str, platform_id: str) -> None:
        """Log in to the Riot Game Client."""
        print(f'Logging in: {username} {platform_id}')
        await self.focus_client_window()
        await sleep_in_seconds(2)

        handler = self._get_window_handler()

        # Navigate to username field and clear it
        for _ in range(4):
            await handler.keyboard_type(Key.Tab)

        for _ in range(10):
            await handler.keyboard_type(Key.Backspace)
        await handler.keyboard_type(username)

        # Navigate to password field and clear it
        await handler.keyboard_type(Key.Tab)

        for _ in range(10):
            await handler.keyboard_type(Key.Backspace)
        await handler.keyboard_type(password)

        # Navigate to login button and press Enter
        for _ in range(7):
            await handler.press_key(Key.Tab)

        await handler.keyboard_type(Key.Enter)
        await handler.keyboard_type(Key.Enter)

    async def is_auto_login_enabled(self) -> Dict[str, Any]:
        """Check if auto login is enabled."""
        return await self._invoke_riot_request(
            await self.get_lockfile_path(),
            '/riotclient/get_auto_login_enabled',
            'GET',
            None,
            0,
        )

    async def get_state(self) -> Dict[str, Any]:
        """Get the current state of the League of Legends client."""
        return await self._invoke_riot_request(
            await self.get_lockfile_path(),
            '/lol-patch/v1/products/league_of_legends/state',
            'GET',
            None,
            0,
        )

    async def get_installs(self) -> Dict[str, Any]:
        """Get installation information."""
        return await self._invoke_riot_request(
            await self.get_lockfile_path(),
            '/patch/v1/installs',
            'GET',
            None,
            30,
        )

    async def get_client_path(self) -> list[str]:
        """Get the path where Riot Client is installed."""
        paths = self.default_client_paths
        for path in paths:
            if os.path.exists(path):
                return [path]
        return []

    async def remove_lockfile(self) -> None:
        """Remove the Riot Client lockfile."""
        try:
            lockfile_path = await self.get_lockfile_path()
            os.unlink(lockfile_path)
        except Exception:
            # Ignore errors if lockfile doesn't exist
            pass

    async def get_lockfile_path(self) -> str:
        """Get the path to the Riot Client lockfile."""
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        return str(Path(local_app_data) / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile')

    def get_lockfile_credentials(self, path: str) -> LockfileCredentials:
        """Extract credentials from lockfile."""
        with open(path, 'r') as f:
            data = f.read()
        parts = data.split(':')
        return LockfileCredentials(port=parts[2], password=parts[3])

    async def start_riot_client(self, region: Region, locale: Locale) -> None:
        """Start the Riot Client with specified region and locale."""
        refined_region = refine_region(region)

        command = [
            self.riot_client_services_path,
            '--launch-product=league_of_legends',
            '--launch-patchline=live',
            f'--region={refined_region.upper()}',
            f'--locale={locale}',
        ]

        try:
            # Start the process
            await asyncio.create_subprocess_shell(
                ' '.join(command),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait a bit for the process to start
            await asyncio.sleep(2)

            # Wait for installation/patching to complete
            await self.get_installs()
            await self.wait_to_patch()

        except Exception as e:
            print(f'Failed to start Riot Client Services: {e}')
            raise

    async def wait_to_patch(self) -> None:
        """Wait for the game to finish patching."""
        max_attempts = 300

        for i in range(max_attempts):
            try:
                status = await self._invoke_riot_request(
                    await self.get_lockfile_path(),
                    '/patch/v1/installs/league_of_legends.live/status',
                    'GET',
                    None,
                    0,
                )

                if status.get('patch', {}).get('state') == 'up_to_date':
                    break

                progress = status.get('patch', {}).get('progress', {}).get('progress', 0)
                print(f'Installing LoL: {progress}%')

            except Exception as e:
                print('Failed to get patch status:', e)

            await sleep_in_seconds(1)

    async def get_region_locale(self, retry: int = 3) -> RegionLocale:
        """Get the current region and locale from the client."""
        response = await self._invoke_riot_request(
            await self.get_lockfile_path(),
            '/riotclient/get_region_locale',
            'GET',
            None,
            retry,
        )

        return RegionLocale(locale=response['locale'], region=response['region'])

    async def focus_client_window(self) -> None:
        """Focus the Riot Client window."""
        target_window_title = 'Riot Client'
        handler = self._get_window_handler()
        await handler.focus_client_window(target_window_title)

    async def _wait_for_lockfile_exists(self, file_path: str, timeout: int = 60000) -> None:
        """Wait for the lockfile to exist."""
        start_time = asyncio.get_event_loop().time()
        timeout_seconds = timeout / 1000

        while not os.path.exists(file_path):
            if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                raise ConfigError(f'File not found: {file_path}')
            await sleep_in_seconds(1)

    async def _invoke_riot_request(
        self,
        lockfile: str,
        path: str,
        method: str = 'GET',
        body: Optional[Dict[str, Any]] = None,
        retry: int = 3,
    ) -> Any:
        """Make an authenticated request to the Riot Client API."""
        await self._wait_for_lockfile_exists(lockfile)

        credentials = self.get_lockfile_credentials(lockfile)
        port = credentials.port
        password = credentials.password
        auth = b64encode(f'riot:{password}'.encode()).decode()

        url = f'https://127.0.0.1:{port}{path}'

        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json',
        }

        response = await make_request(
            method,
            url,
            headers,
            body,
            retry,
        )

        return response

    def _get_window_handler(self) -> WindowHandler:
        """Get or create a WindowHandler instance."""
        if self._window_handler is None:
            self._window_handler = WindowHandler()
        return self._window_handler