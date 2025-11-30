"""Tests for domain entities."""

import pytest

from lol_replay_recorder.domain.entities import Summoner


class TestSummoner:
    """Test cases for Summoner entity."""

    def test_summoner_creation(self):
        """Test creating a summoner with basic information."""
        summoner = Summoner("TestPlayer", "1234")

        assert summoner.summoner_name == "TestPlayer"
        assert summoner.tagline == "1234"
        assert summoner.riot_id == "TestPlayer#1234"
        assert summoner.puuid == ""

    def test_summoner_with_puuid(self):
        """Test creating a summoner with PUUID."""
        puuid = "test-puuid-12345"
        summoner = Summoner("TestPlayer", "1234", puuid)

        assert summoner.summoner_name == "TestPlayer"
        assert summoner.tagline == "1234"
        assert summoner.riot_id == "TestPlayer#1234"
        assert summoner.puuid == puuid

    def test_summoner_riot_id_formatting(self):
        """Test that riot_id is properly formatted with URL encoding."""
        summoner = Summoner("Test Player", "NA1")

        # Space should be encoded as %20
        assert summoner.riot_id == "Test%20Player#NA1"
        assert summoner.summoner_name == "Test Player"
        assert summoner.tagline == "NA1"

    def test_summoner_equality(self):
        """Test summoner equality based on attributes."""
        summoner1 = Summoner("Player", "123", "puuid1")
        summoner2 = Summoner("Player", "123", "puuid1")
        summoner3 = Summoner("Player", "456", "puuid1")

        # Different objects, same attributes
        assert summoner1.summoner_name == summoner2.summoner_name
        assert summoner1.tagline == summoner2.tagline
        assert summoner1.puuid == summoner2.puuid
        assert summoner1.riot_id == summoner2.riot_id

        # Different tagline
        assert summoner2.tagline != summoner3.tagline
        assert summoner2.riot_id != summoner3.riot_id