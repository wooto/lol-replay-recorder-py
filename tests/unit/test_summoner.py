from lol_replay_recorder.models.summoner import Summoner
from urllib.parse import quote


def test_summoner_initialization():
    summoner = Summoner("TestPlayer", "na1", "puuid-123")
    assert summoner.summoner_name == "TestPlayer"
    assert summoner.tagline == "na1"
    assert summoner.puuid == "puuid-123"


def test_summoner_riot_id_generation():
    summoner = Summoner("TestPlayer", "na1")
    expected = f"{quote('TestPlayer')}#na1"
    assert summoner.riot_id == expected


def test_summoner_with_special_characters_in_name():
    summoner = Summoner("Test Player!", "kr")
    assert "Test%20Player%21" in summoner.riot_id
    assert summoner.riot_id.endswith("#kr")


def test_summoner_default_puuid():
    summoner = Summoner("Player", "EUW")
    assert summoner.puuid == ""