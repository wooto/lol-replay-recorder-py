from urllib.parse import quote


class Summoner:
    """Represents a League of Legends summoner."""

    def __init__(self, summoner_name: str, tagline: str, puuid: str = ""):
        self.summoner_name = summoner_name
        self.tagline = tagline
        self.riot_id = f"{quote(summoner_name)}#{tagline}"
        self.puuid = puuid