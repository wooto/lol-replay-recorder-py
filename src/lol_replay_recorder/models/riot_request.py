import httpx
from typing import Any
from ..domain.errors import CustomError, HTTPError


async def make_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    retries: int = 5,
) -> Any:
    """
    Make HTTP request to Riot Replay API.
    The replay API uses self-signed certificates, so we disable SSL verification.
    """
    if retries < 0:
        raise HTTPError(url, 0, "Max retries exceeded")

    new_headers = {**(headers or {}), "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=new_headers,
                json=body if method.upper() != "GET" else None,
            )

            if not response.is_success:
                if response.status_code == 404:
                    raise HTTPError(url, response.status_code, "Failed to find the requested resource.")
                return await make_request(method, url, headers, body, retries - 1)

            try:
                return await response.json()
            except Exception:
                return response

    except CustomError:
        raise
    except Exception as e:
        if retries <= 0:
            raise HTTPError(url, 0, str(e))
        return await make_request(method, url, headers, body, retries - 1)