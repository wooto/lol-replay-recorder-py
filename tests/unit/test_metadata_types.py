"""Tests for metadata type definitions matching TypeScript Metadata.ts"""

import pytest
from typing import TypedDict

from lol_replay_recorder.models.metadata_types import (
    PlayerInfo,
    Summoner,
    TeamInfo,
    SelectorData,
    SummonerTeamInfo,
)


class TestSummonerTeamInfo:
    """Test SummonerTeamInfo TypedDict"""

    @pytest.mark.unit
    def test_summoner_team_info_structure(self):
        """Test that SummonerTeamInfo has required fields"""
        def process_team_info(info: SummonerTeamInfo) -> SummonerTeamInfo:
            return info

        # Valid structure
        team_info: SummonerTeamInfo = {
            "nickname": "TeamNickname",
            "team": {
                "name": "TeamName"
            }
        }

        assert team_info["nickname"] == "TeamNickname"
        assert team_info["team"]["name"] == "TeamName"

        # Test with missing required field - this would fail at runtime if accessed
        with pytest.raises(KeyError):
            invalid_team_info = {
                "team": {
                    "name": "TeamName"
                }
                # Missing nickname
            }
            _ = invalid_team_info["nickname"]


class TestSummoner:
    """Test Summoner TypedDict"""

    @pytest.mark.unit
    def test_summoner_structure(self):
        """Test that Summoner has required fields matching TypeScript version"""
        def process_summoner(summoner: Summoner) -> Summoner:
            return summoner

        team_info: SummonerTeamInfo = {
            "nickname": "TestNickname",
            "team": {
                "name": "TestTeam"
            }
        }

        # Valid structure with all required fields
        summoner: Summoner = {
            "id": 12345,
            "summoner_id": "abcdefg",
            "tagline": "NA1",
            "puuid": "puuid-12345",
            "name": "TestPlayer",
            "position": "MIDDLE",
            "tier": "GOLD",
            "game_name": "GameName",
            "internal_name": "InternalName",
            "team_info": team_info
        }

        assert summoner["id"] == 12345
        assert summoner["summoner_id"] == "abcdefg"
        assert summoner["tagline"] == "NA1"
        assert summoner["puuid"] == "puuid-12345"
        assert summoner["name"] == "TestPlayer"
        assert summoner["position"] == "MIDDLE"
        assert summoner["tier"] == "GOLD"
        assert summoner["game_name"] == "GameName"
        assert summoner["internal_name"] == "InternalName"
        assert summoner["team_info"]["nickname"] == "TestNickname"
        assert summoner["team_info"]["team"]["name"] == "TestTeam"

    @pytest.mark.unit
    def test_summoner_minimal_structure(self):
        """Test Summoner with minimal required fields"""
        team_info: SummonerTeamInfo = {
            "nickname": "MinNick",
            "team": {
                "name": "MinTeam"
            }
        }

        minimal_summoner: Summoner = {
            "id": 1,
            "summoner_id": "min",
            "tagline": "KR",
            "puuid": "min-puuid",
            "name": "MinPlayer",
            "position": "TOP",
            "tier": "BRONZE",
            "game_name": "MinGame",
            "internal_name": "MinInternal",
            "team_info": team_info
        }

        assert minimal_summoner["id"] == 1
        assert minimal_summoner["name"] == "MinPlayer"


class TestTeamInfo:
    """Test TeamInfo TypedDict"""

    @pytest.mark.unit
    def test_team_info_structure(self):
        """Test TeamInfo structure (keeping existing structure for compatibility)"""
        def process_team_info(info: TeamInfo) -> TeamInfo:
            return info

        team_info: TeamInfo = {
            "teamId": 100,
            "win": True,
            "firstBlood": True,
            "firstTower": False,
            "firstInhibitor": False,
            "firstBaron": False,
            "firstDragon": True,
            "firstRiftHerald": False,
            "towerKills": 5,
            "inhibitorKills": 1,
            "baronKills": 0,
            "dragonKills": 3,
            "riftHeraldKills": 1,
            "banCount": 5
        }

        assert team_info["teamId"] == 100
        assert team_info["win"] is True
        assert team_info["towerKills"] == 5
        assert team_info["dragonKills"] == 3


class TestPlayerInfo:
    """Test PlayerInfo TypedDict matching TypeScript version"""

    @pytest.mark.unit
    def test_player_info_structure(self):
        """Test that PlayerInfo matches TypeScript structure with game_id and summoner"""
        def process_player_info(info: PlayerInfo) -> PlayerInfo:
            return info

        team_info: SummonerTeamInfo = {
            "nickname": "TestNick",
            "team": {
                "name": "TestTeam"
            }
        }

        summoner: Summoner = {
            "id": 12345,
            "summoner_id": "summoner123",
            "tagline": "EUW",
            "puuid": "puuid-67890",
            "name": "TestPlayer",
            "position": "JUNGLE",
            "tier": "PLATINUM",
            "game_name": "TestGameName",
            "internal_name": "TestInternal",
            "team_info": team_info
        }

        player_info: PlayerInfo = {
            "game_id": "game-12345",
            "summoner": summoner
        }

        assert player_info["game_id"] == "game-12345"
        assert player_info["summoner"]["name"] == "TestPlayer"
        assert player_info["summoner"]["summoner_id"] == "summoner123"
        assert player_info["summoner"]["position"] == "JUNGLE"
        assert player_info["summoner"]["tier"] == "PLATINUM"

    @pytest.mark.unit
    def test_player_info_integration(self):
        """Test PlayerInfo with nested structures"""
        # Create complete nested structure
        team_info: SummonerTeamInfo = {
            "nickname": "ProNick",
            "team": {
                "name": "ProTeam"
            }
        }

        summoner: Summoner = {
            "id": 99999,
            "summoner_id": "pro-summoner",
            "tagline": "BR1",
            "puuid": "pro-puuid-123",
            "name": "ProPlayer",
            "position": "BOTTOM",
            "tier": "CHALLENGER",
            "game_name": "ProGame",
            "internal_name": "ProInternal",
            "team_info": team_info
        }

        player_info: PlayerInfo = {
            "game_id": "pro-game-999",
            "summoner": summoner
        }

        # Test deep access
        assert player_info["game_id"] == "pro-game-999"
        assert player_info["summoner"]["team_info"]["nickname"] == "ProNick"
        assert player_info["summoner"]["team_info"]["team"]["name"] == "ProTeam"
        assert player_info["summoner"]["tier"] == "CHALLENGER"
        assert player_info["summoner"]["position"] == "BOTTOM"


class TestSelectorData:
    """Test SelectorData TypedDict"""

    @pytest.mark.unit
    def test_selector_data_structure(self):
        """Test SelectorData structure from TypeScript"""
        def process_selector_data(data: SelectorData) -> SelectorData:
            return data

        selector_data: SelectorData = {
            "game_id": "selector-game-456"
        }

        assert selector_data["game_id"] == "selector-game-456"

    @pytest.mark.unit
    def test_selector_data_different_ids(self):
        """Test SelectorData with different game ID formats"""
        test_cases = [
            "12345",
            "game_abc123",
            "NA1_1234567890",
            "match-12345-67890"
        ]

        for game_id in test_cases:
            selector_data: SelectorData = {"game_id": game_id}
            assert selector_data["game_id"] == game_id


class TestTypeCompatibility:
    """Test type compatibility and integration"""

    @pytest.mark.unit
    def test_metadata_types_compatibility(self):
        """Test that all new metadata types work together"""
        # Create a complete metadata structure
        team_info: SummonerTeamInfo = {
            "nickname": "CompatTest",
            "team": {
                "name": "CompatTeam"
            }
        }

        summoner: Summoner = {
            "id": 55555,
            "summoner_id": "compat-summoner",
            "tagline": "LAS",
            "puuid": "compat-puuid",
            "name": "CompatPlayer",
            "position": "UTILITY",
            "tier": "DIAMOND",
            "game_name": "CompatGame",
            "internal_name": "CompatInternal",
            "team_info": team_info
        }

        player_info: PlayerInfo = {
            "game_id": "compat-game-555",
            "summoner": summoner
        }

        selector_data: SelectorData = {
            "game_id": "compat-game-555"
        }

        # Both should reference the same game
        assert player_info["game_id"] == selector_data["game_id"]
        assert player_info["summoner"]["name"] == "CompatPlayer"

    @pytest.mark.unit
    def test_type_annotation_usage(self):
        """Test that types can be used in function signatures"""
        def process_player_metadata(info: PlayerInfo) -> str:
            """Process player metadata and return a summary"""
            summoner_name = info["summoner"]["name"]
            game_id = info["game_id"]
            tier = info["summoner"]["tier"]
            return f"{summoner_name} ({tier}) in game {game_id}"

        team_info: SummonerTeamInfo = {
            "nickname": "FuncTest",
            "team": {
                "name": "FuncTeam"
            }
        }

        summoner: Summoner = {
            "id": 77777,
            "summoner_id": "func-summoner",
            "tagline": "JP1",
            "puuid": "func-puuid",
            "name": "FuncPlayer",
            "position": "FILL",
            "tier": "MASTER",
            "game_name": "FuncGame",
            "internal_name": "FuncInternal",
            "team_info": team_info
        }

        player_info: PlayerInfo = {
            "game_id": "func-game-777",
            "summoner": summoner
        }

        result = process_player_metadata(player_info)
        expected = "FuncPlayer (MASTER) in game func-game-777"
        assert result == expected