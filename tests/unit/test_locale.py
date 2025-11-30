import pytest
from lol_replay_recorder.models.locale import Locale


@pytest.mark.unit
def test_locale_has_korean():
    assert Locale.ko_KR == "ko_KR"


@pytest.mark.unit
def test_locale_has_english_us():
    assert Locale.en_US == "en_US"


@pytest.mark.unit
def test_locale_has_japanese():
    assert Locale.ja_JP == "ja_JP"


@pytest.mark.unit
def test_locale_values_are_strings():
    assert isinstance(Locale.ko_KR.value, str)


@pytest.mark.unit
def test_locale_has_all_expected_locales():
    expected_locales = {
        "ja_JP", "ko_KR", "ar_AE", "cs_CZ", "de_DE", "el_GR",
        "en_AU", "en_GB", "en_PH", "en_SG", "en_US",
        "es_AR", "es_ES", "es_MX", "fr_FR", "hu_HU", "it_IT",
        "pl_PL", "pt_BR", "ro_RO", "ru_RU", "th_TH", "tr_TR",
        "vi_VN", "zh_MY", "zh_TW"
    }
    actual_locales = {locale.value for locale in Locale}
    assert actual_locales == expected_locales