from .custom_error import CustomError
from .locale import Locale
from .riot_types import PlatformId, Region, Cluster
from .summoner import Summoner as SummonerClass
from .metadata_types import (
    PlayerInfo as MetadataPlayerInfo,
    Summoner,
    TeamInfo,
    SelectorData,
    SummonerTeamInfo,
)
from .replay_type import (
    RecordingProperties,
    RenderProperties,
    GameData,
    ReplayMetadata,
    ReplayData,
    ProcessingOptions,
    KeyValuePair,
    RenderSetting,
    GameInfo,
    PlayerInfo as ReplayPlayerInfo,
    TeamInfo as ReplayTeamInfo,
    EventData,
    # Live Game Data Types
    ActivePlayer,
    Item,
    Keystone,
    RuneTree,
    Runes,
    Scores,
    SummonerSpell,
    SummonerSpells,
    Player,
    Event,
    Events,
    GameDetails,
    LiveGameData,
    # Utility types
    Vector3,
    ColorRGBA,
    # Type aliases
    ReplayID,
    PlatformID,
    GameVersion,
    Timestamp,
    FrameRate,
    Resolution,
    FilePath,
    LogLevel,
    # Union types
    RecordingInput,
    RenderInput,
    GameInput,
    LiveGameInput,
)
# HTTP request functions moved to clients/http package
# Backward compatibility wrappers with deprecation warnings

import warnings
from ..clients.http import LCUClient, RiotAPIClient


async def make_request(method: str, url: str, **kwargs):
    """Legacy wrapper for Riot Client request - DEPRECATED

    This function is deprecated and will be removed in a future version.
    Use lol_replay_recorder.clients.http.RiotAPIClient instead.
    """
    warnings.warn(
        "make_request is deprecated. Use lol_replay_recorder.clients.http.RiotAPIClient instead.",
        DeprecationWarning,
        stacklevel=2
    )
    client = RiotAPIClient()

    # Convert legacy signature to new signature
    # Legacy: make_request(method, url, **kwargs)
    # New: client.request(endpoint, method, **kwargs)
    if url.startswith("https://127.0.0.1:2999"):
        endpoint = url.replace("https://127.0.0.1:2999", "")
    else:
        endpoint = url  # fallback for legacy usage

    return await client.request(endpoint, method, **kwargs)


async def make_lcu_request(lockfile_path: str = None, endpoint: str = None, method: str = "GET", **kwargs):
    """Legacy wrapper for LCU request - DEPRECATED

    This function is deprecated and will be removed in a future version.
    Use lol_replay_recorder.clients.http.LCUClient instead.

    Note: Legacy signature was (lockfile_path, endpoint, method), but new
    LCUClient uses (endpoint, method, **kwargs) with lockfile_path set during init.
    """
    warnings.warn(
        "make_lcu_request is deprecated. Use lol_replay_recorder.clients.http.LCUClient instead.",
        DeprecationWarning,
        stacklevel=2
    )

    # Handle both old and new calling patterns
    if endpoint is None and lockfile_path is not None:
        # Called with legacy pattern: make_lcu_request(endpoint, method)
        endpoint = lockfile_path
        lockfile_path = None

    client = LCUClient(lockfile_path=lockfile_path)
    return await client.request(endpoint, method, **kwargs)


# Re-export read_lockfile for backward compatibility
async def read_lockfile(lockfile_path: str):
    """Legacy wrapper for reading lockfile - DEPRECATED

    This function is deprecated and will be removed in a future version.
    Use lol_replay_recorder.clients.http.LCUClient instead.
    """
    warnings.warn(
        "read_lockfile is deprecated. Use lol_replay_recorder.clients.http.LCUClient instead.",
        DeprecationWarning,
        stacklevel=2
    )
    client = LCUClient()
    return await client._read_lockfile(lockfile_path)

__all__ = [
    "CustomError",
    "Locale",
    "PlatformId",
    "Region",
    "Cluster",
    "SummonerClass",
    "Summoner",
    "MetadataPlayerInfo",
    "ReplayPlayerInfo",
    "TeamInfo",
    "ReplayTeamInfo",
    "SelectorData",
    "SummonerTeamInfo",
    "RecordingProperties",
    "RenderProperties",
    "GameData",
    "ReplayMetadata",
    "ReplayData",
    "ProcessingOptions",
    "KeyValuePair",
    "RenderSetting",
    "GameInfo",
    "PlayerInfo",
    "TeamInfo",
    "EventData",
    # Live Game Data Types
    "ActivePlayer",
    "Item",
    "Keystone",
    "RuneTree",
    "Runes",
    "Scores",
    "SummonerSpell",
    "SummonerSpells",
    "Player",
    "Event",
    "Events",
    "GameDetails",
    "LiveGameData",
    # Utility types
    "Vector3",
    "ColorRGBA",
    # Type aliases
    "ReplayID",
    "PlatformID",
    "GameVersion",
    "Timestamp",
    "FrameRate",
    "Resolution",
    "FilePath",
    "LogLevel",
    # Union types
    "RecordingInput",
    "RenderInput",
    "GameInput",
    "LiveGameInput",
    # Backward compatibility functions (deprecated)
    "make_request",
    "make_lcu_request",
    "read_lockfile",
]