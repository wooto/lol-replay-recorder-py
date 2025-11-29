"""Tests for Riot API types."""

import unittest

from lol_replay_recorder.models.riot_types import PlatformId, Region, Cluster


class TestPlatformId(unittest.TestCase):
    """Test PlatformId enum."""

    def test_platform_id_values(self):
        """Test PlatformId enum has correct values."""
        self.assertEqual(PlatformId.NA1.value, "NA1")
        self.assertEqual(PlatformId.EUW1.value, "EUW1")
        self.assertEqual(PlatformId.KR.value, "KR")
        self.assertEqual(PlatformId.EUN1.value, "EUN1")
        self.assertEqual(PlatformId.BR1.value, "BR1")
        self.assertEqual(PlatformId.LA1.value, "LA1")
        self.assertEqual(PlatformId.LA2.value, "LA2")
        self.assertEqual(PlatformId.OC1.value, "OC1")
        self.assertEqual(PlatformId.RU.value, "RU")
        self.assertEqual(PlatformId.TR1.value, "TR1")
        self.assertEqual(PlatformId.JP1.value, "JP1")
        self.assertEqual(PlatformId.PH2.value, "PH2")
        self.assertEqual(PlatformId.SG2.value, "SG2")
        self.assertEqual(PlatformId.TW2.value, "TW2")
        self.assertEqual(PlatformId.VN2.value, "VN2")
        self.assertEqual(PlatformId.TH2.value, "TH2")
        self.assertEqual(PlatformId.ID2.value, "ID2")

    def test_platform_id_count(self):
        """Test PlatformId enum has correct number of values."""
        self.assertEqual(len(PlatformId), 17)


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