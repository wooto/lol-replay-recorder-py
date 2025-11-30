"""Tests for replay type definitions"""

import pytest
from typing import TypedDict

from lol_replay_recorder.models.replay_type import (
    RecordingProperties,
    RenderProperties,
    GameData,
    ReplayMetadata,
    ReplayData,
    ProcessingOptions,
    KeyValuePair,
    RenderSetting,
    GameInfo,
    PlayerInfo,
    TeamInfo,
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
    # Union types
    LiveGameInput,
    validate_typed_dict,
)


class TestRecordingProperties:
    """Test RecordingProperties TypedDict"""

    @pytest.mark.unit
    def test_recording_properties_structure(self):
        """Test that RecordingProperties has required fields"""
        # Test that the TypedDict can be used as a type annotation
        def process_recording(props: RecordingProperties) -> RecordingProperties:
            return props

        # Test explicit validation for missing required fields
        with pytest.raises(KeyError):
            # Missing required field
            invalid_props = {
                "gameId": "12345",
                "platformId": "na1",
                "startTime": 1234567890,
                # Missing endTime
            }
            validate_typed_dict(RecordingProperties, invalid_props)

    @pytest.mark.unit
    def test_recording_properties_valid(self):
        """Test valid RecordingProperties creation"""
        props: RecordingProperties = {
            "gameId": "12345",
            "platformId": "na1",
            "startTime": 1234567890,
            "endTime": 1234567990,
            "gameVersion": "13.1.123.456",
            "gameMode": "CLASSIC",
            "gameType": "MATCHED_GAME",
            "queueId": 420,
            "mapId": 11,
            "participants": [],
            "recordingQuality": "HIGH"
        }

        assert props["gameId"] == "12345"
        assert props["platformId"] == "na1"


class TestRenderProperties:
    """Test RenderProperties TypedDict"""

    @pytest.mark.unit
    def test_render_properties_structure(self):
        """Test that RenderProperties has required fields"""
        def process_render(props: RenderProperties) -> RenderProperties:
            return props

        # Test explicit validation for missing required fields
        with pytest.raises(KeyError):
            # Missing required field
            invalid_props = {
                "outputPath": "/path/to/output",
                # Missing resolution
            }
            validate_typed_dict(RenderProperties, invalid_props)

    @pytest.mark.unit
    def test_render_properties_valid(self):
        """Test valid RenderProperties creation"""
        props: RenderProperties = {
            "outputPath": "/path/to/output.mp4",
            "resolution": "1920x1080",
            "frameRate": 60,
            "bitrate": 5000,
            "codec": "h264",
            "startTime": 0,
            "endTime": 1800,
            "includeAudio": True,
            "audioCodec": "aac",
            "renderQuality": "HIGH"
        }

        assert props["outputPath"] == "/path/to/output.mp4"
        assert props["resolution"] == "1920x1080"


class TestGameData:
    """Test GameData TypedDict"""

    @pytest.mark.unit
    def test_game_data_structure(self):
        """Test that GameData has required fields"""
        def process_game_data(data: GameData) -> GameData:
            return data

        # Test explicit validation for missing required fields
        with pytest.raises(KeyError):
            # Missing required field
            invalid_data = {
                "gameId": "12345",
                # Missing platformId
            }
            validate_typed_dict(GameData, invalid_data)

    @pytest.mark.unit
    def test_game_data_valid(self):
        """Test valid GameData creation"""
        data: GameData = {
            "gameId": "12345",
            "platformId": "na1",
            "gameCreation": 1234567890,
            "gameDuration": 1800,
            "gameVersion": "13.1.123.456",
            "gameMode": "CLASSIC",
            "gameType": "MATCHED_GAME",
            "participants": [],
            "teams": [],
            "events": []
        }

        assert data["gameId"] == "12345"
        assert data["platformId"] == "na1"


class TestAdditionalTypes:
    """Test additional TypedDict classes"""

    @pytest.mark.unit
    def test_replay_metadata(self):
        """Test ReplayMetadata structure"""
        metadata: ReplayMetadata = {
            "title": "My Replay",
            "description": "Description of replay",
            "tags": ["highlight", "kill"],
            "author": "PlayerName",
            "createdAt": 1234567890
        }
        assert metadata["title"] == "My Replay"

    @pytest.mark.unit
    def test_processing_options(self):
        """Test ProcessingOptions structure"""
        options: ProcessingOptions = {
            "skipFrames": True,
            "compressionLevel": 5,
            "threadCount": 4,
            "cacheDirectory": "/tmp/cache",
            "logLevel": "INFO"
        }
        assert options["skipFrames"] is True


class TestLiveGameTypes:
    """Test live game data type definitions"""

    @pytest.mark.unit
    def test_active_player_structure(self):
        """Test ActivePlayer TypedDict"""
        active_player: ActivePlayer = {
            "error": "No active player found"
        }
        assert active_player["error"] == "No active player found"

    @pytest.mark.unit
    def test_item_structure(self):
        """Test Item TypedDict"""
        item: Item = {
            "canUse": True,
            "consumable": False,
            "count": 1,
            "displayName": "Infinity Edge",
            "itemID": 3031,
            "price": 3400,
            "rawDescription": "Test description",
            "rawDisplayName": "Raw Infinity Edge",
            "slot": 0
        }
        assert item["itemID"] == 3031
        assert item["canUse"] is True

    @pytest.mark.unit
    def test_keystone_structure(self):
        """Test Keystone TypedDict"""
        keystone: Keystone = {
            "displayName": "Press the Attack",
            "id": 9951,
            "rawDescription": "Test keystone description",
            "rawDisplayName": "Raw Press the Attack"
        }
        assert keystone["id"] == 9951
        assert keystone["displayName"] == "Press the Attack"

    @pytest.mark.unit
    def test_rune_tree_structure(self):
        """Test RuneTree TypedDict"""
        rune_tree: RuneTree = {
            "displayName": "Precision",
            "id": 8000,
            "rawDescription": "Test rune tree description",
            "rawDisplayName": "Raw Precision"
        }
        assert rune_tree["id"] == 8000
        assert rune_tree["displayName"] == "Precision"

    @pytest.mark.unit
    def test_runes_structure(self):
        """Test Runes TypedDict"""
        keystone: Keystone = {
            "displayName": "Press the Attack",
            "id": 9951,
            "rawDescription": "Test keystone description",
            "rawDisplayName": "Raw Press the Attack"
        }

        primary_tree: RuneTree = {
            "displayName": "Precision",
            "id": 8000,
            "rawDescription": "Test rune tree description",
            "rawDisplayName": "Raw Precision"
        }

        secondary_tree: RuneTree = {
            "displayName": "Domination",
            "id": 8100,
            "rawDescription": "Test rune tree description",
            "rawDisplayName": "Raw Domination"
        }

        runes: Runes = {
            "keystone": keystone,
            "primaryRuneTree": primary_tree,
            "secondaryRuneTree": secondary_tree
        }
        assert runes["keystone"]["id"] == 9951
        assert runes["primaryRuneTree"]["displayName"] == "Precision"

    @pytest.mark.unit
    def test_scores_structure(self):
        """Test Scores TypedDict"""
        scores: Scores = {
            "assists": 5,
            "creepScore": 150,
            "deaths": 2,
            "kills": 8,
            "wardScore": 12
        }
        assert scores["kills"] == 8
        assert scores["assists"] == 5
        assert scores["creepScore"] == 150

    @pytest.mark.unit
    def test_summoner_spell_structure(self):
        """Test SummonerSpell TypedDict"""
        spell: SummonerSpell = {
            "displayName": "Flash",
            "rawDescription": "Test flash description",
            "rawDisplayName": "Raw Flash"
        }
        assert spell["displayName"] == "Flash"

    @pytest.mark.unit
    def test_summoner_spells_structure(self):
        """Test SummonerSpells TypedDict"""
        spell1: SummonerSpell = {
            "displayName": "Flash",
            "rawDescription": "Test flash description",
            "rawDisplayName": "Raw Flash"
        }

        spell2: SummonerSpell = {
            "displayName": "Ignite",
            "rawDescription": "Test ignite description",
            "rawDisplayName": "Raw Ignite"
        }

        spells: SummonerSpells = {
            "summonerSpellOne": spell1,
            "summonerSpellTwo": spell2
        }
        assert spells["summonerSpellOne"]["displayName"] == "Flash"
        assert spells["summonerSpellTwo"]["displayName"] == "Ignite"

    @pytest.mark.unit
    def test_player_structure(self):
        """Test Player TypedDict - comprehensive test"""
        # Create nested structures
        item: Item = {
            "canUse": True,
            "consumable": False,
            "count": 1,
            "displayName": "Infinity Edge",
            "itemID": 3031,
            "price": 3400,
            "rawDescription": "Test description",
            "rawDisplayName": "Raw Infinity Edge",
            "slot": 0
        }

        keystone: Keystone = {
            "displayName": "Press the Attack",
            "id": 9951,
            "rawDescription": "Test keystone description",
            "rawDisplayName": "Raw Press the Attack"
        }

        rune_tree: RuneTree = {
            "displayName": "Precision",
            "id": 8000,
            "rawDescription": "Test rune tree description",
            "rawDisplayName": "Raw Precision"
        }

        runes: Runes = {
            "keystone": keystone,
            "primaryRuneTree": rune_tree,
            "secondaryRuneTree": rune_tree
        }

        scores: Scores = {
            "assists": 5,
            "creepScore": 150,
            "deaths": 2,
            "kills": 8,
            "wardScore": 12
        }

        spell: SummonerSpell = {
            "displayName": "Flash",
            "rawDescription": "Test flash description",
            "rawDisplayName": "Raw Flash"
        }

        spells: SummonerSpells = {
            "summonerSpellOne": spell,
            "summonerSpellTwo": spell
        }

        player: Player = {
            "championName": "Yasuo",
            "isBot": False,
            "isDead": False,
            "items": [item],
            "level": 12,
            "riotIdGameName": "PlayerOne",
            "position": "MIDDLE",
            "rawChampionName": "Yasuo",
            "rawSkinName": "SkinName",
            "respawnTimer": 0,
            "runes": runes,
            "scores": scores,
            "screenPositionBottom": "0,0",
            "screenPositionCenter": "0,0",
            "skinID": 1,
            "skinName": "Default",
            "summonerName": "TestPlayer",
            "summonerSpells": spells,
            "team": "ORDER"
        }

        assert player["championName"] == "Yasuo"
        assert player["level"] == 12
        assert player["isBot"] is False
        assert player["items"][0]["itemID"] == 3031
        assert player["runes"]["keystone"]["id"] == 9951
        assert player["scores"]["kills"] == 8
        assert player["summonerSpells"]["summonerSpellOne"]["displayName"] == "Flash"

    @pytest.mark.unit
    def test_event_structure(self):
        """Test Event TypedDict"""
        event: Event = {
            "EventID": 1001,
            "EventName": "ChampionKill",
            "EventTime": 12345,
            "Assisters": ["Player2", "Player3"],
            "KillerName": "Player1",
            "VictimName": "Player4",
            "KillStreak": 3
        }
        assert event["EventID"] == 1001
        assert event["EventName"] == "ChampionKill"
        assert event["KillerName"] == "Player1"
        assert len(event["Assisters"]) == 2

    @pytest.mark.unit
    def test_event_minimal_structure(self):
        """Test Event TypedDict with minimal required fields"""
        event: Event = {
            "EventID": 1002,
            "EventName": "LevelUp",
            "EventTime": 12346
        }
        assert event["EventID"] == 1002
        assert event["EventName"] == "LevelUp"

    @pytest.mark.unit
    def test_events_structure(self):
        """Test Events TypedDict"""
        event1: Event = {
            "EventID": 1001,
            "EventName": "ChampionKill",
            "EventTime": 12345
        }

        event2: Event = {
            "EventID": 1002,
            "EventName": "LevelUp",
            "EventTime": 12346
        }

        events: Events = {
            "Events": [event1, event2]
        }
        assert len(events["Events"]) == 2
        assert events["Events"][0]["EventName"] == "ChampionKill"

    @pytest.mark.unit
    def test_game_details_structure(self):
        """Test GameDetails TypedDict"""
        game_details: GameDetails = {
            "gameMode": "CLASSIC",
            "gameTime": 1800,
            "mapName": "Summoner's Rift",
            "mapNumber": 11,
            "mapTerrain": "Default"
        }
        assert game_details["gameMode"] == "CLASSIC"
        assert game_details["gameTime"] == 1800
        assert game_details["mapName"] == "Summoner's Rift"

    @pytest.mark.unit
    def test_live_game_data_structure(self):
        """Test LiveGameData TypedDict - integration test"""
        # Minimal structures for testing
        active_player: ActivePlayer = {"error": ""}

        keystone: Keystone = {
            "displayName": "Press the Attack",
            "id": 9951,
            "rawDescription": "Test",
            "rawDisplayName": "Test"
        }

        rune_tree: RuneTree = {
            "displayName": "Precision",
            "id": 8000,
            "rawDescription": "Test",
            "rawDisplayName": "Test"
        }

        runes: Runes = {
            "keystone": keystone,
            "primaryRuneTree": rune_tree,
            "secondaryRuneTree": rune_tree
        }

        scores: Scores = {
            "assists": 0,
            "creepScore": 0,
            "deaths": 0,
            "kills": 0,
            "wardScore": 0
        }

        spell: SummonerSpell = {
            "displayName": "Flash",
            "rawDescription": "Test",
            "rawDisplayName": "Test"
        }

        spells: SummonerSpells = {
            "summonerSpellOne": spell,
            "summonerSpellTwo": spell
        }

        player: Player = {
            "championName": "Yasuo",
            "isBot": False,
            "isDead": False,
            "items": [],
            "level": 1,
            "riotIdGameName": "Test",
            "position": "MIDDLE",
            "rawChampionName": "Yasuo",
            "rawSkinName": "Test",
            "respawnTimer": 0,
            "runes": runes,
            "scores": scores,
            "screenPositionBottom": "0,0",
            "screenPositionCenter": "0,0",
            "skinID": 0,
            "skinName": "Test",
            "summonerName": "Test",
            "summonerSpells": spells,
            "team": "ORDER"
        }

        events: Events = {"Events": []}

        game_details: GameDetails = {
            "gameMode": "CLASSIC",
            "gameTime": 0,
            "mapName": "Summoner's Rift",
            "mapNumber": 11,
            "mapTerrain": "Default"
        }

        live_game_data: LiveGameData = {
            "activePlayer": active_player,
            "allPlayers": [player],
            "events": events,
            "gameData": game_details
        }

        assert live_game_data["activePlayer"]["error"] == ""
        assert len(live_game_data["allPlayers"]) == 1
        assert live_game_data["allPlayers"][0]["championName"] == "Yasuo"
        assert live_game_data["gameData"]["gameMode"] == "CLASSIC"

    @pytest.mark.unit
    def test_utility_types(self):
        """Test utility types Vector3 and ColorRGBA"""
        vector3: Vector3 = {
            "x": 1.0,
            "y": 2.5,
            "z": -0.5
        }
        assert vector3["x"] == 1.0
        assert vector3["z"] == -0.5

        color: ColorRGBA = {
            "r": 1.0,
            "g": 0.5,
            "b": 0.0,
            "a": 0.8
        }
        assert color["r"] == 1.0
        assert color["a"] == 0.8

    @pytest.mark.unit
    def test_type_compatibility(self):
        """Test that new types are compatible with existing union types"""
        def process_live_game_input(data: LiveGameInput) -> LiveGameInput:
            return data

        # This should work with string input
        result = process_live_game_input("test_input")
        assert result == "test_input"

        # This should work with LiveGameData input
        active_player: ActivePlayer = {"error": ""}
        events: Events = {"Events": []}
        game_details: GameDetails = {
            "gameMode": "CLASSIC",
            "gameTime": 0,
            "mapName": "Test",
            "mapNumber": 11,
            "mapTerrain": "Test"
        }

        live_data: LiveGameData = {
            "activePlayer": active_player,
            "allPlayers": [],
            "events": events,
            "gameData": game_details
        }

        result = process_live_game_input(live_data)
        assert result == live_data