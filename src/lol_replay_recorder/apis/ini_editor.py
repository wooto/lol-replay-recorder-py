import configparser
from typing import Any


class IniEditor:
    """Editor for INI configuration files."""

    def __init__(self, filename: str):
        self.filename = filename
        self.data = self._load_ini()

    def _load_ini(self) -> dict[str, dict[str, Any]]:
        """Load INI file and return as nested dict."""
        try:
            # Check if file exists
            from pathlib import Path
            if not Path(self.filename).exists():
                raise FileNotFoundError(f"INI file not found: {self.filename}")

            config = configparser.ConfigParser()
            config.optionxform = str  # type: ignore[assignment]  # Preserve case of keys
            result = config.read(self.filename)

            # Check if file was successfully read
            if not result:
                raise Exception(f"Failed to read INI file: {self.filename}")

            # Convert to dict for easier manipulation
            return {section: dict(config[section]) for section in config.sections()}
        except Exception as e:
            raise Exception(f"Failed to load INI file: {str(e)}")

    def save(self) -> None:
        """Save current data back to INI file."""
        config = configparser.ConfigParser()
        config.optionxform = str  # type: ignore[assignment]  # Preserve case of keys
        for section, values in self.data.items():
            config[section] = values

        with open(self.filename, "w", encoding="utf-8") as f:
            config.write(f, space_around_delimiters=False)

    def update_section(self, section: str, key: str, value: Any) -> None:
        """Update or create a section with key-value pair."""
        if section not in self.data:
            self.data[section] = {}
        self.data[section][key] = str(value)