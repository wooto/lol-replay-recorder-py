"""
Domain types package.

This package contains type definitions, TypedDict classes, enums, and other
type-related constructs used throughout the application.
"""

from .locale import Locale
from .metadata_types import (
    PlayerInfo as MetadataPlayerInfo,
    SelectorData,
    Summoner as MetadataSummoner,
    SummonerTeamInfo,
    TeamDetails,
    TeamInfo,
)
from .replay_types import (
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
    LogLevel,
    Player,
    PlayerInfo,
    ProcessingOptions,
    RecordingInput,
    RecordingProperties,
    RenderProperties,
    ReplayData,
    ReplayID,
    ReplayMetadata,
    Runes,
    RuneTree,
    Scores,
    SummonerSpell,
    SummonerSpells,
    TeamInfo as ReplayTeamInfo,
    Timestamp,
    Vector3,
)
from .riot_types import Cluster, PlatformId, Region

__all__ = [
    # Locale
    "Locale",
    # Riot Types
    "PlatformId",
    "Region",
    "Cluster",
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
    "TeamInfo",
    "EventData",
    # Type aliases
    "ReplayID",
    "GameVersion",
    "Timestamp",
    "FrameRate",
    "LogLevel",
    "RecordingInput",
    "GameInput",
    "LiveGameInput",
    # Live Game Types
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
    # Utility Types
    "Vector3",
    "ColorRGBA",
    # Metadata Types
    "SummonerTeamInfo",
    "TeamDetails",
    "MetadataSummoner",
    "MetadataPlayerInfo",
    "SelectorData",
    # Teams (avoid conflicts)
    "ReplayTeamInfo",
]