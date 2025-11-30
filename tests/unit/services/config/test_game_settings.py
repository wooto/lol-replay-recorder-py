"""Tests for GameSettingsManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lol_replay_recorder.models.locale import Locale
from lol_replay_recorder.services.config.game_settings import GameSettingsManager
from lol_replay_recorder.services.process.platform import PlatformResolver
from lol_replay_recorder.domain.errors import CustomError


class TestGameSettingsManager:
    """Test cases for GameSettingsManager."""

    def test_init_with_default_factories(self):
        """Test initialization with default factories."""
        platform_resolver = MagicMock(spec=PlatformResolver)

        manager = GameSettingsManager(platform_resolver)

        assert manager.platform == platform_resolver
        assert manager.create_ini_editor is not None
        assert manager.create_yaml_editor is not None

    def test_init_with_custom_factories(self):
        """Test initialization with custom factories."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        custom_ini_factory = MagicMock()
        custom_yaml_factory = MagicMock()

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=custom_ini_factory,
            yaml_editor_factory=custom_yaml_factory
        )

        assert manager.platform == platform_resolver
        assert manager.create_ini_editor == custom_ini_factory
        assert manager.create_yaml_editor == custom_yaml_factory

    @pytest.mark.asyncio
    async def test_set_locale_success(self):
        """Test successful locale setting."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_product_settings_path.return_value = "/path/to/settings.yaml"

        mock_yaml_editor = MagicMock()
        mock_yaml_editor.data = {
            "locale_data": {
                "available_locales": ["en_US", "ko_KR"]
            }
        }
        yaml_editor_factory = MagicMock(return_value=mock_yaml_editor)

        manager = GameSettingsManager(
            platform_resolver,
            yaml_editor_factory=yaml_editor_factory
        )

        await manager.set_locale(Locale.ko_KR)

        yaml_editor_factory.assert_called_once_with("/path/to/settings.yaml")
        mock_yaml_editor.update.assert_any_call("locale_data.default_locale", "ko_KR")
        mock_yaml_editor.update.assert_any_call("settings.locale", "ko_KR")
        mock_yaml_editor.save_changes.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_locale_invalid_locale(self):
        """Test setting invalid locale raises CustomError."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_product_settings_path.return_value = "/path/to/settings.yaml"

        mock_yaml_editor = MagicMock()
        mock_yaml_editor.data = {
            "locale_data": {
                "available_locales": ["en_US", "ko_KR"]
            }
        }
        yaml_editor_factory = MagicMock(return_value=mock_yaml_editor)

        manager = GameSettingsManager(
            platform_resolver,
            yaml_editor_factory=yaml_editor_factory
        )

        with pytest.raises(CustomError, match="Invalid locale: zh_TW"):
            await manager.set_locale(Locale.zh_TW)

    @pytest.mark.asyncio
    async def test_set_locale_handles_exceptions(self):
        """Test set_locale handles general exceptions gracefully."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_product_settings_path.return_value = "/path/to/settings.yaml"

        yaml_editor_factory = MagicMock(side_effect=Exception("File not found"))

        manager = GameSettingsManager(
            platform_resolver,
            yaml_editor_factory=yaml_editor_factory
        )

        # Should not raise exception, but print error
        with patch('builtins.print') as mock_print:
            await manager.set_locale(Locale.ko_KR)
            mock_print.assert_called_once_with("Error setting locale: File not found")

    @pytest.mark.asyncio
    async def test_update_game_config_single_file(self):
        """Test updating game configuration for single config file."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install/path"]
        platform_resolver.get_config_file_path.return_value = "/path/to/game.cfg"

        mock_ini_editor = MagicMock()
        ini_editor_factory = MagicMock(return_value=mock_ini_editor)

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        updates = {
            "General.EnableReplayApi": True,
            "Audio.MasterVolume": 0.8
        }

        await manager.update_game_config(updates)

        ini_editor_factory.assert_called_once_with("/path/to/game.cfg")
        mock_ini_editor.update.assert_any_call("General.EnableReplayApi", True)
        mock_ini_editor.update.assert_any_call("Audio.MasterVolume", 0.8)
        mock_ini_editor.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_game_config_multiple_files(self):
        """Test updating game configuration for multiple config files."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install1", "/install2"]
        platform_resolver.get_config_file_path.side_effect = ["/path/to/game1.cfg", "/path/to/game2.cfg"]

        mock_ini_editor1 = MagicMock()
        mock_ini_editor2 = MagicMock()
        ini_editor_factory = MagicMock(side_effect=[mock_ini_editor1, mock_ini_editor2])

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        updates = {"General.EnableReplayApi": True}

        await manager.update_game_config(updates)

        assert ini_editor_factory.call_count == 2
        ini_editor_factory.assert_any_call("/path/to/game1.cfg")
        ini_editor_factory.assert_any_call("/path/to/game2.cfg")
        mock_ini_editor1.update.assert_called_once_with("General.EnableReplayApi", True)
        mock_ini_editor2.update.assert_called_once_with("General.EnableReplayApi", True)
        mock_ini_editor1.save.assert_called_once()
        mock_ini_editor2.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_game_config_no_section_default(self):
        """Test updating config without section defaults to General."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install/path"]
        platform_resolver.get_config_file_path.return_value = "/path/to/game.cfg"

        mock_ini_editor = MagicMock()
        ini_editor_factory = MagicMock(return_value=mock_ini_editor)

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        updates = {"EnableReplayApi": True}

        await manager.update_game_config(updates)

        mock_ini_editor.update_section.assert_called_once_with("General", "EnableReplayApi", True)

    @pytest.mark.asyncio
    async def test_update_game_config_handles_exceptions(self):
        """Test update_game_config handles exceptions gracefully."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install/path"]
        platform_resolver.get_config_file_path.return_value = "/path/to/game.cfg"

        ini_editor_factory = MagicMock(side_effect=Exception("Permission denied"))

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        with patch('builtins.print') as mock_print:
            await manager.update_game_config({"General.EnableReplayApi": True})
            mock_print.assert_called_once_with(
                "Error updating config file /path/to/game.cfg: Permission denied"
            )

    @pytest.mark.asyncio
    async def test_set_window_mode_enable(self):
        """Test enabling window mode."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install/path"]
        platform_resolver.get_config_file_path.return_value = "/path/to/game.cfg"

        mock_ini_editor = MagicMock()
        ini_editor_factory = MagicMock(return_value=mock_ini_editor)

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        await manager.set_window_mode(True)

        ini_editor_factory.assert_called_once_with("/path/to/game.cfg")
        mock_ini_editor.update.assert_any_call("General.WindowMode", "1")
        mock_ini_editor.update.assert_any_call("General.Borderless", "1")
        mock_ini_editor.update.assert_any_call("General.Fullscreen", "0")
        mock_ini_editor.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_window_mode_disable(self):
        """Test disabling window mode."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install/path"]
        platform_resolver.get_config_file_path.return_value = "/path/to/game.cfg"

        mock_ini_editor = MagicMock()
        ini_editor_factory = MagicMock(return_value=mock_ini_editor)

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        await manager.set_window_mode(False)

        ini_editor_factory.assert_called_once_with("/path/to/game.cfg")
        mock_ini_editor.update.assert_any_call("General.WindowMode", "0")
        mock_ini_editor.update.assert_any_call("General.Borderless", "0")
        mock_ini_editor.update.assert_any_call("General.Fullscreen", "1")
        mock_ini_editor.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_window_mode_handles_exceptions(self):
        """Test set_window_mode handles exceptions gracefully."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install/path"]
        platform_resolver.get_config_file_path.return_value = "/path/to/game.cfg"

        ini_editor_factory = MagicMock(side_effect=Exception("File access error"))

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        with patch('builtins.print') as mock_print:
            await manager.set_window_mode(True)
            mock_print.assert_called_once_with(
                "Error setting window mode in config file /path/to/game.cfg: File access error"
            )

    @pytest.mark.asyncio
    async def test_set_window_mode_multiple_files(self):
        """Test setting window mode for multiple config files."""
        platform_resolver = MagicMock(spec=PlatformResolver)
        platform_resolver.get_installed_paths.return_value = ["/install1", "/install2"]
        platform_resolver.get_config_file_path.side_effect = ["/path/to/game1.cfg", "/path/to/game2.cfg"]

        mock_ini_editor1 = MagicMock()
        mock_ini_editor2 = MagicMock()
        ini_editor_factory = MagicMock(side_effect=[mock_ini_editor1, mock_ini_editor2])

        manager = GameSettingsManager(
            platform_resolver,
            ini_editor_factory=ini_editor_factory
        )

        await manager.set_window_mode(True)

        assert ini_editor_factory.call_count == 2
        mock_ini_editor1.update.assert_any_call("General.WindowMode", "1")
        mock_ini_editor2.update.assert_any_call("General.WindowMode", "1")
        mock_ini_editor1.save.assert_called_once()
        mock_ini_editor2.save.assert_called_once()