import httpx
import base64
import asyncio
from pathlib import Path
from typing import Any
from ..domain.errors import CustomError, HTTPError, LockfileError


async def read_lockfile(lockfile_path: str) -> dict[str, str]:
    """
    Read League Client lockfile and extract credentials.
    Format: LeagueClient:PID:PORT:PASSWORD:PROTOCOL
    """
    # Wait for lockfile to exist
    path = Path(lockfile_path)
    timeout = 60  # seconds
    elapsed = 0

    while not path.exists() and elapsed < timeout:
        await asyncio.sleep(1)
        elapsed += 1

    if not path.exists():
        raise LockfileError(f"Lockfile not found: {lockfile_path}")

    content = path.read_text(encoding="utf-8")
    parts = content.split(":")

    return {
        "port": parts[2],
        "password": parts[3],
    }


async def make_lcu_request(
    lockfile_path: str,
    endpoint: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    retries: int = 3,
) -> Any:
    """
    Make authenticated request to League Client Update (LCU) API.
    Uses credentials from lockfile.
    """
    credentials = await read_lockfile(lockfile_path)
    port = credentials["port"]
    password = credentials["password"]

    # Create basic auth header
    auth_string = f"riot:{password}"
    auth_bytes = auth_string.encode("utf-8")
    auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = f"https://127.0.0.1:{port}{endpoint}"
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method.upper() != "GET" else None,
            )

            if not response.is_success:
                if retries <= 0:
                    raise HTTPError(
                        url,
                        response.status_code,
                        f"LCU Request Error: {response.status_code} {response.reason_phrase}"
                    )
                return await make_lcu_request(
                    lockfile_path, endpoint, method, body, retries - 1
                )

            try:
                return response.json()
            except Exception:
                return response

    except Exception as e:
        if retries <= 0:
            raise HTTPError(url, 0, f"LCU Request Error: {str(e)}")
        return await make_lcu_request(
            lockfile_path, endpoint, method, body, retries - 1
        )