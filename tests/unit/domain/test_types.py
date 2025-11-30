"""Tests for domain types."""

import pytest

from lol_replay_recorder.domain.types import (
    Locale,
    PlatformId,
    Region,
    Cluster,
    RecordingProperties,
    RenderProperties,
    ReplayID,
    GameVersion,
    Timestamp,
)


class TestEnums:
    """Test enum types."""

    def test_locale_values(self):
        """Test that Locale enum has expected values."""
        assert Locale.ko_KR == "ko_KR"
        assert Locale.en_US == "en_US"
        assert Locale.ja_JP == "ja_JP"
        assert Locale.zh_TW == "zh_TW"

    def test_platform_id_values(self):
        """Test that PlatformId enum has expected values."""
        assert PlatformId.NA1 == "na1"
        assert PlatformId.KR == "kr"
        assert PlatformId.EUW1 == "euw1"
        assert PlatformId.EUNE1 == "eun1"

    def test_type_aliases(self):
        """Test that type aliases work correctly."""
        # Type aliases should work as regular types
        region: Region = "americas"
        cluster: Cluster = "na1"
        replay_id: ReplayID = "test-replay-id"
        game_version: GameVersion = "13.5.1"
        timestamp: Timestamp = 1678886400

        assert isinstance(region, str)
        assert isinstance(cluster, str)
        assert isinstance(replay_id, str)
        assert isinstance(game_version, str)
        assert isinstance(timestamp, int)


class TestTypedDict:
    """Test TypedDict types."""

    def test_recording_properties_structure(self):
        """Test RecordingProperties structure."""
        recording: RecordingProperties = {
            "gameId": "12345",
            "platformId": "kr",
            "startTime": 1678886400,
            "endTime": 1678890000,
            "gameVersion": "13.5.1",
            "gameMode": "CLASSIC",
            "gameType": "MATCHED_GAME",
            "queueId": 420,
            "mapId": 11,
            "participants": [],
            "recordingQuality": "high",
        }

        assert recording["gameId"] == "12345"
        assert recording["platformId"] == "kr"
        assert recording["recordingQuality"] == "high"

    def test_render_properties_structure(self):
        """Test RenderProperties structure."""
        render: RenderProperties = {
            "outputPath": "/path/to/output.mp4",
            "resolution": "1920x1080",
            "frameRate": 60,
            "bitrate": 5000,
            "codec": "h264",
            "startTime": 0,
            "endTime": 300,
            "includeAudio": True,
            "audioCodec": "aac",
            "renderQuality": "high",
        }

        assert render["outputPath"] == "/path/to/output.mp4"
        assert render["resolution"] == "1920x1080"
        assert render["frameRate"] == 60
        assert render["includeAudio"] is True