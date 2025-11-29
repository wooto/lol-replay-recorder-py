"""Metadata type definitions matching TypeScript Metadata.ts"""

from __future__ import annotations

from typing import TypedDict, NotRequired


class SummonerTeamInfo(TypedDict):
    """Team information within a summoner's metadata"""
    nickname: str
    team: TeamDetails


class TeamDetails(TypedDict):
    """Team details information"""
    name: str


class Summoner(TypedDict):
    """Complete summoner information matching TypeScript version"""
    id: int
    summoner_id: str
    tagline: str
    puuid: str
    name: str
    position: str
    tier: str
    game_name: str
    internal_name: str
    team_info: SummonerTeamInfo


class PlayerInfo(TypedDict):
    """Player information matching TypeScript version"""
    game_id: str
    summoner: Summoner


class SelectorData(TypedDict):
    """Selector data matching TypeScript version"""
    game_id: str


# Re-export TeamInfo from replay_types for compatibility
from .replay_type import TeamInfo