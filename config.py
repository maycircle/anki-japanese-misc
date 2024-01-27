from typing import Any, Generic, Optional, TypeVar

from aqt import gui_hooks
from aqt import mw
from aqt.addons import AbortAddonImport

ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)

_configNeedsUpdate = False


class ConfigABC:
    data: dict[str, Any]

    def __init__(self):
        if mw is None:
            raise AbortAddonImport("No Anki main window")
        self._load()

    def _load(self):
        global _configNeedsUpdate
        self.data = mw.addonManager.getConfig(__name__)  # type: ignore
        _configNeedsUpdate = False

    def get(self, key: str) -> Any:
        if _configNeedsUpdate:
            self._load()
        return self.data[key]

    def set(self, key: str, value: Any):
        self.data[key] = value
        mw.addonManager.writeConfig(__name__, self.data)


T = TypeVar("T")


class property(Generic[T]):
    def __set_name__(self, owner, name):
        self.propName = name

    def __init__(self, t: Optional[type[T]] = None):
        pass

    def __get__(self, obj: ConfigABC, objtype=None) -> T:
        return obj.get(self.propName)

    def __set__(self, obj: ConfigABC, value: T):
        obj.set(self.propName, value)


class Config(ConfigABC):
    openingPitchClassname = property(str)
    continuousPitchClassname = property(str)
    closingPitchClassname = property(str)
    useSpansOverTags = property(bool)


def _configWillUpdate(text: str, addon: str) -> str:
    if addon != ADDON_PACKAGE:
        return text

    global _configNeedsUpdate
    _configNeedsUpdate = True
    return text


gui_hooks.addon_config_editor_will_update_json.append(_configWillUpdate)
