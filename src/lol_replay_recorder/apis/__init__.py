# Backward compatibility imports - these have been moved to services/config/editors/
import warnings

from ..services.config.editors.ini import IniEditor
from ..services.config.editors.yaml import YamlEditor

warnings.warn(
    "Importing from 'lol_replay_recorder.apis' is deprecated. "
    "Use 'lol_replay_recorder.services.config.editors' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["IniEditor", "YamlEditor"]
