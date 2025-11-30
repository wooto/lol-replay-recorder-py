"""INI configuration editor."""

import configparser
from typing import Any, Optional
from ....domain.errors import ConfigError
from ....protocols.config_editor import ConfigEditor


class IniEditor(ConfigEditor):
    """Editor for INI configuration files."""

    def __init__(self, filename: str):
        self.filename = filename
        self._data = {}
        self.load(filename)

    def load(self, file_path: Optional[str] = None) -> None:
        """Load INI file and return as nested dict."""
        target_file = file_path or self.filename
        if not target_file:
            raise ConfigError("No file path specified")

        try:
            # Check if file exists
            from pathlib import Path
            if not Path(target_file).exists():
                raise FileNotFoundError(f"INI file not found: {target_file}")

            config = configparser.ConfigParser()
            config.optionxform = str  # type: ignore[assignment]  # Preserve case of keys
            result = config.read(target_file)

            # Check if file was successfully read
            if not result:
                raise ConfigError(f"Failed to read INI file: {target_file}")

            # Convert to dict for easier manipulation
            self._data = {section: dict(config[section]) for section in config.sections()}
        except Exception as e:
            raise ConfigError(f"Failed to load INI file: {str(e)}")

    def save(self, file_path: Optional[str] = None) -> None:
        """Save current data back to INI file."""
        target_file = file_path or self.filename
        if not target_file:
            raise ConfigError("No file path specified")

        config = configparser.ConfigParser()
        config.optionxform = str  # type: ignore[assignment]  # Preserve case of keys
        for section, values in self._data.items():
            config[section] = values

        with open(target_file, "w", encoding="utf-8") as f:
            config.write(f, space_around_delimiters=False)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value by key."""
        parts = key.split(".", 1)  # Split into section and key
        if len(parts) != 2:
            return default

        section, key_name = parts
        return self._data.get(section, {}).get(key_name, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        parts = key.split(".", 1)  # Split into section and key
        if len(parts) != 2:
            raise ConfigError(f"Invalid INI path format: {key}. Expected 'section.key'")

        section, key_name = parts
        if section not in self._data:
            self._data[section] = {}
        self._data[section][key_name] = str(value)

    def update(self, updates: dict) -> None:
        """Update multiple configuration values."""
        for key, value in updates.items():
            self.set(key, value)

    def has(self, key: str) -> bool:
        """Check if configuration key exists."""
        return self.get(key) is not None

    def delete(self, key: str) -> None:
        """Delete configuration key."""
        parts = key.split(".", 1)  # Split into section and key
        if len(parts) != 2:
            return

        section, key_name = parts
        if section in self._data and key_name in self._data[section]:
            del self._data[section][key_name]
            # Remove section if empty
            if not self._data[section]:
                del self._data[section]

    @property
    def data(self) -> dict:
        """Get the raw configuration data."""
        return self._data.copy()

    @data.setter
    def data(self, value: dict) -> None:
        """Set the raw configuration data."""
        self._data = dict(value)

    # Legacy methods for backward compatibility
    def update_section(self, section: str, key: str, value: Any) -> None:
        """Update or create a section with key-value pair."""
        self.set(f"{section}.{key}", value)