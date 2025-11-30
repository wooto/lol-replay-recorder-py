import pytest
from pathlib import Path
from lol_replay_recorder.services.config.editors.yaml import YamlEditor


@pytest.fixture
def temp_yaml_file(tmp_path):
    """Create a temporary YAML file for testing."""
    yaml_content = """locale_data:
  default_locale: en_US
  available_locales:
    - en_US
    - ko_KR
    - ja_JP
settings:
  locale: en_US
  region: na1
"""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)
    return str(yaml_file)


@pytest.mark.unit
def test_yaml_editor_loads_file(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    assert editor.filename == temp_yaml_file
    assert "locale_data" in editor.data
    assert editor.data["locale_data"]["default_locale"] == "en_US"


@pytest.mark.unit
def test_yaml_editor_update_nested_path(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    editor.update("locale_data.default_locale", "ko_KR")
    assert editor.data["locale_data"]["default_locale"] == "ko_KR"


@pytest.mark.unit
def test_yaml_editor_update_creates_missing_keys(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    editor.update("new_section.new_key", "new_value")
    assert editor.data["new_section"]["new_key"] == "new_value"


@pytest.mark.unit
def test_yaml_editor_save_changes(temp_yaml_file):
    editor = YamlEditor(temp_yaml_file)
    editor.update("settings.locale", "ja_JP")
    editor.save_changes()

    # Read file and verify changes
    editor2 = YamlEditor(temp_yaml_file)
    assert editor2.data["settings"]["locale"] == "ja_JP"


@pytest.mark.unit
def test_yaml_editor_handles_nonexistent_file():
    with pytest.raises(Exception) as exc_info:
        YamlEditor("/nonexistent/path/file.yaml")
    assert "Failed to load YAML file" in str(exc_info.value)