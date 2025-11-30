"""Protocol for configuration editors."""

from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class ConfigEditor(Protocol):
    """Protocol for configuration file editors."""

    def load(self) -> dict[str, Any]:
        """Load configuration data from file.

        Returns:
            Configuration data as dictionary.

        Raises:
            ConfigError: If loading fails.
        """
        ...

    def save(self) -> None:
        """Save current configuration data to file.

        Raises:
            ConfigError: If saving fails.
        """
        ...

    def update(self, path: str, value: Any) -> None:
        """Update a configuration value using dot notation path.

        Args:
            path: Dot notation path to the value (e.g., "section.key" or "nested.key").
            value: New value to set.
        """
        ...