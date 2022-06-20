"""Host Add-ons for Voice Assistant components.

Add-ons:
 - are added by wrapping methods of different Voice Assistant components
 - can be conditionally added by integrations e.g. if Spotify integration
   is active, music volume will go down when VA is listening or talking
"""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, List

from voiceassistant.utils.log import get_logger

from .create import Addon, CoreAttribute

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


_LOGGER = get_logger(__name__)


AddonStorageType = Dict[CoreAttribute, List[Addon]]

_ADDONS_START: AddonStorageType = {}
_ADDONS_END: AddonStorageType = {}


class AddonsComponent:
    """Addons Component."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        self._vass = vass

        global _ADDONS_START, _ADDONS_END
        _ADDONS_START = {}
        _ADDONS_END = {}

    def add(self, addon: Addon) -> None:
        """Enable addon by wrapping one of methods in core object."""
        if addon.at_start:
            if addon.core_attr not in _ADDONS_START:
                _ADDONS_START[addon.core_attr] = []

            _ADDONS_START[addon.core_attr].append(addon)
        else:
            if addon.core_attr not in _ADDONS_END:
                _ADDONS_END[addon.core_attr] = []

            _ADDONS_END[addon.core_attr].append(addon)
        _LOGGER.info(f"Addon added: {addon.name}")


def expose(attr: CoreAttribute) -> Callable:
    """Expose one of voice assistant methods for addons."""

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore  # TODO
            for addon in _ADDONS_START.get(attr, []):
                addon.func(self._vass)

            result = func(self, *args, **kwargs)

            for addon in _ADDONS_END.get(attr, []):
                addon.func(self._vass)

            return result

        return inner

    return wrapper


__all__ = ["AddonsComponent", "CoreAttribute", "expose"]
