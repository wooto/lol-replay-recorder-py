"""
Protocol definitions for configuration editor implementations.

This module provides protocol interfaces to standardize configuration editing
behavior across different file formats (INI, YAML, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ConfigEditor(ABC):
    """
    Protocol defining the interface for configuration editor implementations.

    This protocol standardizes configuration editing operations, supporting
    various file formats and dot-notation access for nested keys.
    """

    @abstractmethod
    def load(self, file_path: str) -> None:
        """
        Load configuration from file.

        Args:
            file_path: Path to the configuration file

        Raises:
            ConfigEditorError: When loading fails
        """
        pass

    @abstractmethod
    def save(self, file_path: str) -> None:
        """
        Save configuration to file.

        Args:
            file_path: Path to save the configuration file

        Raises:
            ConfigEditorError: When saving fails
        """
        pass

    @abstractmethod
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get configuration value by key.

        Supports dot notation for nested keys (e.g., "section.key").

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.

        Supports dot notation for nested keys (e.g., "section.key").

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        pass

    @abstractmethod
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.

        Args:
            updates: Dictionary of key-value pairs to update
        """
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.

        Args:
            key: Configuration key (supports dot notation)

        Returns:
            True if key exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete configuration key.

        Args:
            key: Configuration key (supports dot notation)
        """
        pass

    @property
    @abstractmethod
    def data(self) -> Dict[str, Any]:
        """Get the raw configuration data."""
        pass

    @data.setter
    @abstractmethod
    def data(self, value: Dict[str, Any]) -> None:
        """Set the raw configuration data."""
        pass


class ConfigEditorError(Exception):
    """Base exception for configuration editor errors."""
    pass