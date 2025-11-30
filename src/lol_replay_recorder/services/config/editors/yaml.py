"""YAML configuration editor."""

import yaml
from typing import Any, Optional
from ....domain.errors import ConfigError
from ....protocols.config_editor import ConfigEditor


class YamlEditor(ConfigEditor):
    """Editor for YAML configuration files."""

    def __init__(self, filename: str):
        self.filename = filename
        self._data = {}
        self.load(filename)

    def load(self, file_path: Optional[str] = None) -> None:
        """Load YAML file and return as dict."""
        target_file = file_path or self.filename
        if not target_file:
            raise ConfigError("No file path specified")

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigError(f"Failed to load YAML file: {str(e)}")

    def save(self, file_path: Optional[str] = None) -> None:
        """Save current data back to YAML file."""
        target_file = file_path or self.filename
        if not target_file:
            raise ConfigError("No file path specified")

        try:
            with open(target_file, "w", encoding="utf-8") as f:
                yaml.dump(self._data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigError(f"Failed to save YAML file: {str(e)}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value by key."""
        keys = key.split(".")
        current = self._data

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        keys = key.split(".")
        current = self._data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def update(self, updates: dict) -> None:
        """Update multiple configuration values."""
        for key, value in updates.items():
            self.set(key, value)

    def has(self, key: str) -> bool:
        """Check if configuration key exists."""
        return self.get(key) is not None

    def delete(self, key: str) -> None:
        """Delete configuration key."""
        keys = key.split(".")
        current = self._data

        # Navigate to parent of key to delete
        for k in keys[:-1]:
            if k not in current:
                return
            current = current[k]

        # Delete the key if it exists
        if keys[-1] in current:
            del current[keys[-1]]

    @property
    def data(self) -> dict:
        """Get the raw configuration data."""
        return self._data.copy()

    @data.setter
    def data(self, value: dict) -> None:
        """Set the raw configuration data."""
        self._data = dict(value)

    # Legacy methods for backward compatibility
    def update_legacy(self, path: str, value: Any) -> None:
        """Update a nested value using dot notation path. Legacy method."""
        self.set(path, value)

    def save_changes(self) -> None:
        """Save changes to file. Alias for save() for backward compatibility."""
        self.save()