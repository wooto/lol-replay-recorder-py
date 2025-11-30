"""Configuration editor factory."""

from .ini import IniEditor
from .yaml import YamlEditor


class ConfigEditorFactory:
    """Factory for creating configuration editors."""

    def create_ini_editor(self, path: str) -> IniEditor:
        """Create an INI editor for the given path."""
        return IniEditor(path)

    def create_yaml_editor(self, path: str) -> YamlEditor:
        """Create a YAML editor for the given path."""
        return YamlEditor(path)