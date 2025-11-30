"""Configuration editors for lol-replay-recorder."""

from .ini import IniEditor
from .yaml import YamlEditor

__all__ = ["IniEditor", "YamlEditor"]