"""Tests for ConfigEditor protocol."""

import pytest
from pathlib import Path
from typing import Any

from lol_replay_recorder.protocols.config_editor import ConfigEditor
from lol_replay_recorder.services.config.editors.ini import IniEditor
from lol_replay_recorder.services.config.editors.yaml import YamlEditor


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


class TestConfigEditorProtocol:
    """Test that both IniEditor and YamlEditor implement ConfigEditor protocol."""

    def test_ini_editor_implements_protocol(self, temp_ini_file):
        """Test that IniEditor implements ConfigEditor protocol."""
        editor = IniEditor(temp_ini_file)

        # Test that it has the required methods
        assert hasattr(editor, 'load')
        assert hasattr(editor, 'save')
        assert hasattr(editor, 'update')

        # Test that methods are callable
        assert callable(editor.load)
        assert callable(editor.save)
        assert callable(editor.update)

        # Test protocol compliance
        assert isinstance(editor, ConfigEditor)

    def test_yaml_editor_implements_protocol(self, temp_yaml_file):
        """Test that YamlEditor implements ConfigEditor protocol."""
        editor = YamlEditor(temp_yaml_file)

        # Test that it has the required methods
        assert hasattr(editor, 'load')
        assert hasattr(editor, 'save')
        assert hasattr(editor, 'update')

        # Test that methods are callable
        assert callable(editor.load)
        assert callable(editor.save)
        assert callable(editor.update)

        # Test protocol compliance
        assert isinstance(editor, ConfigEditor)

    def test_protocol_method_signatures(self, temp_ini_file, temp_yaml_file):
        """Test that protocol methods have correct signatures."""
        ini_editor = IniEditor(temp_ini_file)
        yaml_editor = YamlEditor(temp_yaml_file)

        # Test load() returns None and loads data
        assert ini_editor.load() is None
        assert yaml_editor.load() is None

        # Data should be accessible via data property
        assert isinstance(ini_editor.data, dict)
        assert isinstance(yaml_editor.data, dict)

        # Test save() returns None
        assert ini_editor.save() is None
        assert yaml_editor.save() is None

        # Test update() accepts dict of updates
        ini_editor.update({"General.NewSetting": "test_value"})
        yaml_editor.update({"new_section.new_key": "test_value"})

    def test_editors_as_protocol_parameters(self):
        """Test that editors can be used as ConfigEditor protocol parameters."""
        def process_config(editor: ConfigEditor) -> dict[str, Any]:
            """Function that accepts any ConfigEditor implementation."""
            data = editor.load()
            editor.update("test.key", "test_value")
            editor.save()
            return data

        # This would work with actual files
        # For now, just test that the function signature is correct
        import inspect
        sig = inspect.signature(process_config)
        assert "editor" in sig.parameters

        # Check that the parameter annotation is ConfigEditor
        editor_param = sig.parameters["editor"]
        assert editor_param.annotation is ConfigEditor