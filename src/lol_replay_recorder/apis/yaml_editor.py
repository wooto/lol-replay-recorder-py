import yaml
from typing import Any


class YamlEditor:
    """Editor for YAML configuration files."""

    def __init__(self, filename: str):
        self.filename = filename
        self.data = self._load_yaml()

    def _load_yaml(self) -> dict[str, Any]:
        """Load YAML file and return as dict."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise Exception(f"Failed to load YAML file: {str(e)}")

    def _save_yaml(self) -> None:
        """Save current data back to YAML file."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True)
            print(f"YAML file saved to {self.filename}")
        except Exception as e:
            raise Exception(f"Failed to save YAML file: {str(e)}")

    def update(self, path: str, value: Any) -> None:
        """Update a nested value using dot notation path."""
        keys = path.split(".")
        current = self.data

        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def save_changes(self) -> None:
        """Save changes to file."""
        self._save_yaml()