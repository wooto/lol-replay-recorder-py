"""Replay type definitions for recording and rendering"""

from __future__ import annotations

from typing import TypedDict, List, Dict, Any, Union
from typing_extensions import NotRequired


def validate_typed_dict(typed_dict_class: type, data: Dict[str, Any]) -> None:
    """
    Validate that a dictionary contains all required keys for a TypedDict.

    Args:
        typed_dict_class: The TypedDict class to validate against
        data: The dictionary to validate

    Raises:
        KeyError: If required keys are missing
    """
    required_keys: set[str] = getattr(typed_dict_class, '__required_keys__', set())
    missing_keys = required_keys - data.keys()
    if missing_keys:
        missing_key = next(iter(missing_keys))  # Get first missing key
        raise KeyError(missing_key)


class RecordingProperties(TypedDict):
    """Properties for recording replays"""
    gameId: str
    platformId: str
    startTime: int
    endTime: int
    gameVersion: str
    gameMode: str
    gameType: str
    queueId: int
    mapId: int
    participants: List[Dict[str, Any]]
    recordingQuality: str


class RenderProperties(TypedDict):
    """Properties for rendering replays"""
    outputPath: str
    resolution: str
    frameRate: int
    bitrate: int
    codec: str
    startTime: int
    endTime: int
    includeAudio: bool
    audioCodec: str
    renderQuality: str


class GameData(TypedDict):
    """Core game data structure"""
    gameId: str
    platformId: str
    gameCreation: int
    gameDuration: int
    gameVersion: str
    gameMode: str
    gameType: str
    participants: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]
    events: List[Dict[str, Any]]


class ReplayMetadata(TypedDict):
    """Metadata for replay files"""
    title: str
    description: str
    tags: List[str]
    author: str
    createdAt: int


class ReplayData(TypedDict):
    """Complete replay data structure"""
    metadata: ReplayMetadata
    recording: RecordingProperties
    render: RenderProperties
    gameData: GameData
    processingOptions: ProcessingOptions


class ProcessingOptions(TypedDict):
    """Options for processing replay data"""
    skipFrames: bool
    compressionLevel: int
    threadCount: int
    cacheDirectory: str
    logLevel: str


class KeyValuePair(TypedDict):
    """Key-value pair for generic data storage"""
    key: str
    value: Any


class RenderSetting(TypedDict):
    """Individual render settings"""
    name: str
    value: Union[str, int, float, bool]
    description: NotRequired[str]


class GameInfo(TypedDict):
    """Game information extracted from API"""
    gameId: str
    platformId: str
    gameCreation: int
    gameDuration: int
    queueId: int
    mapId: int
    seasonId: int
    gameVersion: str
    gameMode: str
    gameType: str
    participants: List[PlayerInfo]
    teams: List[TeamInfo]
    participantsCount: int


class PlayerInfo(TypedDict):
    """Player information"""
    participantId: int
    teamId: int
    championId: int
    championName: str
    role: str
    lane: str
    summonerName: str
    summonerId: str
    summonerLevel: int
    profileIconId: int
    kills: int
    deaths: int
    assists: int
    goldEarned: int
    totalDamageDealt: int
    totalMinionsKilled: int
    wardsPlaced: int
    win: bool


class TeamInfo(TypedDict):
    """Team information"""
    teamId: int
    win: bool
    firstBlood: bool
    firstTower: bool
    firstInhibitor: bool
    firstBaron: bool
    firstDragon: bool
    firstRiftHerald: bool
    towerKills: int
    inhibitorKills: int
    baronKills: int
    dragonKills: int
    riftHeraldKills: int
    banCount: int


class EventData(TypedDict):
    """Game event data"""
    timestamp: int
    eventType: str
    participantId: NotRequired[int]
    killerId: NotRequired[int]
    victimId: NotRequired[int]
    assistingParticipantIds: NotRequired[List[int]]
    position: NotRequired[Dict[str, int]]
    itemId: NotRequired[int]
    skillSlot: NotRequired[int]
    levelUpType: NotRequired[str]
    monsterType: NotRequired[str]
    buildingType: NotRequired[str]
    towerType: NotRequired[str]
    laneType: NotRequired[str]
    data: NotRequired[Dict[str, Any]]


# Type aliases for common usage
ReplayID = str
PlatformID = str
GameVersion = str
Timestamp = int
FrameRate = int
Resolution = str
FilePath = str
LogLevel = str


# Live Game Data Types - Critical for real-time game data capture

class ActivePlayer(TypedDict):
    """Active player in the game"""
    error: str


class Item(TypedDict):
    """Item information for a player"""
    canUse: bool
    consumable: bool
    count: int
    displayName: str
    itemID: int
    price: int
    rawDescription: str
    rawDisplayName: str
    slot: int


class Keystone(TypedDict):
    """Keystone rune information"""
    displayName: str
    id: int
    rawDescription: str
    rawDisplayName: str


class RuneTree(TypedDict):
    """Rune tree information"""
    displayName: str
    id: int
    rawDescription: str
    rawDisplayName: str


class Runes(TypedDict):
    """Player rune configuration"""
    keystone: Keystone
    primaryRuneTree: RuneTree
    secondaryRuneTree: RuneTree


class Scores(TypedDict):
    """Player score statistics"""
    assists: int
    creepScore: int
    deaths: int
    kills: int
    wardScore: int


class SummonerSpell(TypedDict):
    """Summoner spell information"""
    displayName: str
    rawDescription: str
    rawDisplayName: str


class SummonerSpells(TypedDict):
    """Player summoner spells"""
    summonerSpellOne: SummonerSpell
    summonerSpellTwo: SummonerSpell


class Player(TypedDict):
    """Complete player information for live game"""
    championName: str
    isBot: bool
    isDead: bool
    items: List[Item]
    level: int
    riotIdGameName: str
    position: str
    rawChampionName: str
    rawSkinName: str
    respawnTimer: int
    runes: Runes
    scores: Scores
    screenPositionBottom: str
    screenPositionCenter: str
    skinID: int
    skinName: str
    summonerName: str
    summonerSpells: SummonerSpells
    team: str


class Event(TypedDict):
    """Game event information"""
    EventID: int
    EventName: str
    EventTime: int
    Assisters: NotRequired[List[str]]
    KillerName: NotRequired[str]
    VictimName: NotRequired[str]
    KillStreak: NotRequired[int]


class Events(TypedDict):
    """Collection of game events"""
    Events: List[Event]


class GameDetails(TypedDict):
    """Live game details"""
    gameMode: str
    gameTime: int
    mapName: str
    mapNumber: int
    mapTerrain: str


class LiveGameData(TypedDict):
    """Complete live game data structure"""
    activePlayer: ActivePlayer
    allPlayers: List[Player]
    events: Events
    gameData: GameDetails


# Additional utility types from TypeScript
class Vector3(TypedDict):
    """3D vector coordinates"""
    x: float
    y: float
    z: float


class ColorRGBA(TypedDict):
    """RGBA color values"""
    r: float
    g: float
    b: float
    a: float


# Union types for flexible input
RecordingInput = Union[str, int, RecordingProperties]
RenderInput = Union[str, RenderProperties]
GameInput = Union[str, int, GameData]
LiveGameInput = Union[str, LiveGameData]