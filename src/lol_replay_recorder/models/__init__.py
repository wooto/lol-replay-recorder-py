# Legacy imports from new domain structure with deprecation warnings
import warnings

# Import from new domain structure
from ..domain.entities import Summoner as DomainSummoner
from ..domain.types import (
    ActivePlayer,
    ColorRGBA,
    Event,
    EventData,
    Events,
    FrameRate,
    GameData,
    GameDetails,
    GameInfo,
    GameInput,
    GameVersion,
    Item,
    Keystone,
    KeyValuePair,
    LiveGameData,
    LiveGameInput,
    Locale,
    LogLevel,
    MetadataPlayerInfo,
    MetadataSummoner,
    PlatformId,
    Player,
    PlayerInfo,
    ProcessingOptions,
    RecordingInput,
    RecordingProperties,
    RenderProperties,
    ReplayData,
    ReplayID,
    ReplayMetadata,
    ReplayTeamInfo,
    Runes,
    RuneTree,
    Scores,
    SelectorData,
    SummonerSpell,
    SummonerSpells,
    SummonerTeamInfo,
    TeamDetails,
    TeamInfo,
    Timestamp,
    Vector3,
)
from ..domain.types.riot_types import Cluster, Region
from ..domain.errors import CustomError

# Backward compatibility aliases with deprecation warnings
class SummonerClass(DomainSummoner):
    """Legacy Summoner class - DEPRECATED

    Use lol_replay_recorder.domain.entities.Summoner instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SummonerClass is deprecated. Use lol_replay_recorder.domain.entities.Summoner instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

# Create aliases for backward compatibility
Summoner = MetadataSummoner
ReplayPlayerInfo = PlayerInfo
# HTTP request functions moved to clients/http package
# Backward compatibility wrappers with deprecation warnings

import warnings
from ..clients.http import LCUClient, RiotAPIClient
from ..constants import RIOT_REPLAY_BASE_URL


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
    if url.startswith(RIOT_REPLAY_BASE_URL):
        endpoint = url.replace(RIOT_REPLAY_BASE_URL, "")
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
    # Errors
    "CustomError",
    # Types
    "Locale",
    "PlatformId",
    "Region",
    "Cluster",
    # Entities
    "SummonerClass",
    # Metadata Types
    "Summoner",
    "MetadataPlayerInfo",
    "ReplayPlayerInfo",
    "TeamInfo",
    "ReplayTeamInfo",
    "SelectorData",
    "SummonerTeamInfo",
    "TeamDetails",
    # Replay Types
    "RecordingProperties",
    "RenderProperties",
    "GameData",
    "ReplayMetadata",
    "ReplayData",
    "ProcessingOptions",
    "KeyValuePair",
    "GameInfo",
    "PlayerInfo",
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
    "GameVersion",
    "Timestamp",
    "FrameRate",
    "LogLevel",
    # Union types
    "RecordingInput",
    "GameInput",
    "LiveGameInput",
    # Backward compatibility functions (deprecated)
    "make_request",
    "make_lcu_request",
    "read_lockfile",
]