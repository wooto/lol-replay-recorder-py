"""Riot API platform IDs and region types.

This module defines the platform IDs and region/cluster type aliases
used by the Riot Games API.
"""

from enum import Enum
from typing import TypeAlias


class PlatformId(str, Enum):
    """Riot Games platform IDs.

    Platform IDs are used to identify specific game servers and regions
    in Riot Games API requests. Each platform ID corresponds to a specific
    geographic region.

    Examples:
        >>> PlatformId.NA1
        'na1'
        >>> PlatformId.EUW1
        'euw1'
    """

    NA1 = "na1"
    EUW1 = "euw1"
    EUNE1 = "eun1"  # Fixed name from EUN1 to EUNE1 to match TypeScript
    KR = "kr"
    BR1 = "br1"
    LA1 = "la1"
    LA2 = "la2"
    OC1 = "oc1"
    RU = "ru"
    TR1 = "tr1"
    JP1 = "jp1"
    PH2 = "ph2"
    SG2 = "sg2"
    TW2 = "tw2"
    VN2 = "vn2"
    TH2 = "th2"
    # Additional platform IDs from TypeScript reference
    EUROPE = "europe"
    ASIA = "asia"
    SEA = "sea"
    AMERICAS = "americas"
    AP = "ap"
    BR = "br"
    EU = "eu"
    NA = "na"
    LATAM = "latam"
    ESPORTS = "esports"
    APAC = "apac"


# Type aliases for Riot API region and cluster identifiers
Region: TypeAlias = str
Cluster: TypeAlias = str