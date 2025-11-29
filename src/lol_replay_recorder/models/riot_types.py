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
        'NA1'
        >>> PlatformId.EUW1
        'EUW1'
    """

    NA1 = "NA1"
    EUW1 = "EUW1"
    KR = "KR"
    EUN1 = "EUN1"
    BR1 = "BR1"
    LA1 = "LA1"
    LA2 = "LA2"
    OC1 = "OC1"
    RU = "RU"
    TR1 = "TR1"
    JP1 = "JP1"
    PH2 = "PH2"
    SG2 = "SG2"
    TW2 = "TW2"
    VN2 = "VN2"
    TH2 = "TH2"
    ID2 = "ID2"


# Type aliases for Riot API region and cluster identifiers
Region: TypeAlias = str
Cluster: TypeAlias = str