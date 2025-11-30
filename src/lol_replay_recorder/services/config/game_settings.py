"""Game settings management service."""

from typing import Any

from ...models.locale import Locale
from ...domain.errors import CustomError
from ...services.process.platform import PlatformResolver
from .editors.yaml import YamlEditor
from .editors.ini import IniEditor


class GameSettingsManager:
    """게임 설정 관리."""

    def __init__(
        self,
        platform_resolver: PlatformResolver,
        ini_editor_factory: type[IniEditor] = IniEditor,
        yaml_editor_factory: type[YamlEditor] = YamlEditor,
    ):
        self.platform = platform_resolver
        self.create_ini_editor = ini_editor_factory
        self.create_yaml_editor = yaml_editor_factory

    async def set_locale(self, locale: Locale) -> None:
        """LeagueClient.set_locale() 이동."""
        try:
            yaml_path = self.platform.get_product_settings_path()
            yaml_editor = self.create_yaml_editor(yaml_path)

            available_locales = yaml_editor.data.get("locale_data", {}).get("available_locales", [])
            if locale not in available_locales:
                raise CustomError(
                    f"Invalid locale: {locale}, available locales: {available_locales}"
                )

            yaml_editor.update("locale_data.default_locale", locale)
            yaml_editor.update("settings.locale", locale)
            yaml_editor.save_changes()

        except Exception as e:
            if isinstance(e, CustomError):
                raise
            print(f"Error setting locale: {e}")

    async def update_game_config(
        self,
        updates: dict[str, Any]
    ) -> None:
        """LeagueClient.update_game_config() 이동."""
        config_paths = self._get_config_file_paths()

        for config_path in config_paths:
            try:
                editor = self.create_ini_editor(config_path)

                # Apply updates using dot notation or section.key format
                for path, value in updates.items():
                    if "." in path:
                        # Use dot notation for nested updates
                        editor.update(path, value)
                    else:
                        # For INI files, assume it's a section.key pair
                        if "." in path:
                            editor.update(path, value)
                        else:
                            # If no section provided, default to 'General' section
                            editor.update_section("General", path, value)

                editor.save()

            except Exception as e:
                print(f"Error updating config file {config_path}: {e}")

    def _get_config_file_paths(self) -> list[str]:
        """Get all game.cfg file paths from installed locations."""
        installed_paths = self.platform.get_installed_paths()
        config_paths = []

        for install_path in installed_paths:
            config_path = self.platform.get_config_file_path(install_path)
            if config_path:
                config_paths.append(config_path)

        return config_paths

    async def set_window_mode(
        self,
        enable: bool
    ) -> None:
        """LeagueClient.set_window_mode() 이동."""
        config_paths = self._get_config_file_paths()

        for config_path in config_paths:
            try:
                editor = self.create_ini_editor(config_path)

                # Update window mode settings
                window_mode_updates = {
                    "General.WindowMode": "1" if enable else "0",
                    "General.Borderless": "1" if enable else "0",
                    "General.Fullscreen": "0" if enable else "1"
                }

                for path, value in window_mode_updates.items():
                    editor.update(path, value)

                editor.save()

            except Exception as e:
                print(f"Error setting window mode in config file {config_path}: {e}")