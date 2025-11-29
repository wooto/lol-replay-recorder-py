"""Replay type definitions for recording and rendering"""

from __future__ import annotations

from typing import TypedDict, List, Dict, Any, Optional, NotRequired, Union


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


# Union types for flexible input
RecordingInput = Union[str, int, RecordingProperties]
RenderInput = Union[str, RenderProperties]
GameInput = Union[str, int, GameData]