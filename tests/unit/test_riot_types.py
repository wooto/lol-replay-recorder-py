"""Tests for Riot API types."""

import unittest

from lol_replay_recorder.models.riot_types import PlatformId, Region, Cluster


class TestPlatformId(unittest.TestCase):
    """Test PlatformId enum."""

    def test_platform_id_values(self):
        """Test PlatformId enum has correct values."""
        self.assertEqual(PlatformId.NA1.value, "na1")
        self.assertEqual(PlatformId.EUW1.value, "euw1")
        self.assertEqual(PlatformId.KR.value, "kr")
        self.assertEqual(PlatformId.EUNE1.value, "eun1")  # Updated name from EUN1 to EUNE1
        self.assertEqual(PlatformId.BR1.value, "br1")
        self.assertEqual(PlatformId.LA1.value, "la1")
        self.assertEqual(PlatformId.LA2.value, "la2")
        self.assertEqual(PlatformId.OC1.value, "oc1")
        self.assertEqual(PlatformId.RU.value, "ru")
        self.assertEqual(PlatformId.TR1.value, "tr1")
        self.assertEqual(PlatformId.JP1.value, "jp1")
        self.assertEqual(PlatformId.PH2.value, "ph2")
        self.assertEqual(PlatformId.SG2.value, "sg2")
        self.assertEqual(PlatformId.TW2.value, "tw2")
        self.assertEqual(PlatformId.VN2.value, "vn2")
        self.assertEqual(PlatformId.TH2.value, "th2")

        # Test additional cluster and regional platform IDs
        self.assertEqual(PlatformId.EUROPE.value, "europe")
        self.assertEqual(PlatformId.ASIA.value, "asia")
        self.assertEqual(PlatformId.SEA.value, "sea")
        self.assertEqual(PlatformId.AMERICAS.value, "americas")
        self.assertEqual(PlatformId.AP.value, "ap")
        self.assertEqual(PlatformId.BR.value, "br")
        self.assertEqual(PlatformId.EU.value, "eu")
        self.assertEqual(PlatformId.NA.value, "na")
        self.assertEqual(PlatformId.LATAM.value, "latam")
        self.assertEqual(PlatformId.ESPORTS.value, "esports")
        self.assertEqual(PlatformId.APAC.value, "apac")

    def test_platform_id_count(self):
        """Test PlatformId enum has correct number of values."""
        self.assertEqual(len(PlatformId), 27)


class TestTypeAliases(unittest.TestCase):
    """Test type aliases."""

    def test_region_alias(self):
        """Test Region type alias."""
        # Region should be a string
        self.assertIs(str, Region)

    def test_cluster_alias(self):
        """Test Cluster type alias."""
        # Cluster should be a string
        self.assertIs(str, Cluster)


if __name__ == "__main__":
    unittest.main()