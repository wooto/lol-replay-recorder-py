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
    EventData
)


class TestRecordingProperties:
    """Test RecordingProperties TypedDict"""

    def test_recording_properties_structure(self):
        """Test that RecordingProperties has required fields"""
        # Test that the TypedDict can be used as a type annotation
        def process_recording(props: RecordingProperties) -> RecordingProperties:
            return props

        # This should fail at runtime if the structure is wrong
        with pytest.raises(KeyError):
            # Missing required field
            invalid_props = {
                "gameId": "12345",
                "platformId": "NA1",
                "startTime": 1234567890,
                # Missing endTime
            }
            process_recording(invalid_props)

    def test_recording_properties_valid(self):
        """Test valid RecordingProperties creation"""
        props: RecordingProperties = {
            "gameId": "12345",
            "platformId": "NA1",
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
        assert props["platformId"] == "NA1"


class TestRenderProperties:
    """Test RenderProperties TypedDict"""

    def test_render_properties_structure(self):
        """Test that RenderProperties has required fields"""
        def process_render(props: RenderProperties) -> RenderProperties:
            return props

        with pytest.raises(KeyError):
            # Missing required field
            invalid_props = {
                "outputPath": "/path/to/output",
                # Missing resolution
            }
            process_render(invalid_props)

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

    def test_game_data_structure(self):
        """Test that GameData has required fields"""
        def process_game_data(data: GameData) -> GameData:
            return data

        with pytest.raises(KeyError):
            # Missing required field
            invalid_data = {
                "gameId": "12345",
                # Missing platformId
            }
            process_game_data(invalid_data)

    def test_game_data_valid(self):
        """Test valid GameData creation"""
        data: GameData = {
            "gameId": "12345",
            "platformId": "NA1",
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
        assert data["platformId"] == "NA1"


class TestAdditionalTypes:
    """Test additional TypedDict classes"""

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