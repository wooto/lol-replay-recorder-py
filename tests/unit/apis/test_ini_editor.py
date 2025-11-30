import pytest
from pathlib import Path
from lol_replay_recorder.apis.ini_editor import IniEditor


@pytest.fixture
def temp_ini_file(tmp_path):
    """Create a temporary INI file for testing."""
    ini_content = """[General]
EnableReplayApi=1
GameMouseSpeed=10

[HUD]
ShowTimestamps=1
"""
    ini_file = tmp_path / "test.ini"
    ini_file.write_text(ini_content)
    return str(ini_file)


@pytest.mark.unit
def test_ini_editor_loads_file(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    assert editor.filename == temp_ini_file
    assert "General" in editor.data
    assert editor.data["General"]["EnableReplayApi"] == "1"


@pytest.mark.unit
def test_ini_editor_update_section(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    editor.update_section("General", "EnableReplayApi", "0")
    assert editor.data["General"]["EnableReplayApi"] == "0"


@pytest.mark.unit
def test_ini_editor_create_new_section(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    editor.update_section("NewSection", "NewKey", "NewValue")
    assert "NewSection" in editor.data
    assert editor.data["NewSection"]["NewKey"] == "NewValue"


@pytest.mark.unit
def test_ini_editor_save(temp_ini_file):
    editor = IniEditor(temp_ini_file)
    editor.update_section("General", "EnableReplayApi", "0")
    editor.save()

    # Read file and verify changes
    editor2 = IniEditor(temp_ini_file)
    assert editor2.data["General"]["EnableReplayApi"] == "0"


@pytest.mark.unit
def test_ini_editor_handles_nonexistent_file():
    with pytest.raises(Exception) as exc_info:
        IniEditor("/nonexistent/path/file.ini")
    assert "Failed to load INI file" in str(exc_info.value)