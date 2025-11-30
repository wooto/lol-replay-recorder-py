"""Tests for ConfigEditorFactory."""

import pytest
from unittest.mock import patch, MagicMock

from lol_replay_recorder.services.config.editors.factory import ConfigEditorFactory
from lol_replay_recorder.services.config.editors.ini import IniEditor
from lol_replay_recorder.services.config.editors.yaml import YamlEditor


class TestConfigEditorFactory:
    """Test cases for ConfigEditorFactory."""

    def test_create_ini_editor(self):
        """Test creating an INI editor."""
        factory = ConfigEditorFactory()

        with patch('lol_replay_recorder.services.config.editors.factory.IniEditor') as mock_ini_editor:
            result = factory.create_ini_editor("/path/to/config.ini")

            mock_ini_editor.assert_called_once_with("/path/to/config.ini")
            assert result == mock_ini_editor.return_value

    def test_create_yaml_editor(self):
        """Test creating a YAML editor."""
        factory = ConfigEditorFactory()

        with patch('lol_replay_recorder.services.config.editors.factory.YamlEditor') as mock_yaml_editor:
            result = factory.create_yaml_editor("/path/to/config.yaml")

            mock_yaml_editor.assert_called_once_with("/path/to/config.yaml")
            assert result == mock_yaml_editor.return_value