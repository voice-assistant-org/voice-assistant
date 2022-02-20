"""Host add-on creation tools."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

from voiceassistant.utils.log import get_logger

_LOGGER = get_logger(__name__)


if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


class CoreAttribute(Enum):
    """Store paths to attributes of core VoiceAssistant object."""

    SPEECH_PROCESSING = ("interfaces", "speech", "process_speech")
    SPEECH_OUTPUT = ("interfaces", "speech", "output")
    KEYWORD_WAIT = (
        "interfaces",
        "speech",
        "_wait_for_trigger",
    )


class Addon:
    """Voice Assistant Add-on representation."""

    def __init__(
        self,
        func: Callable[[VoiceAssistant], None],
        core_attr: CoreAttribute,
        at_start: bool,
        name: Optional[str] = None,
    ):
        self._func = func
        self.core_attr = core_attr
        self.at_start = at_start
        self.name = name or self.func.__name__

    def func(self, vass: VoiceAssistant) -> None:
        """Call addon function but handle any errors."""
        try:
            self._func(vass)
        except Exception:
            _LOGGER.exception("Addon exception")


def addon_begin(core_attr: CoreAttribute, name: Optional[str] = None) -> Callable:
    """Wrap add-on begin function into Addon object."""

    def wrapper(func: Callable[[VoiceAssistant], None]) -> Addon:
        return Addon(func, core_attr, at_start=True, name=name)

    return wrapper


def addon_end(core_attr: CoreAttribute, name: Optional[str] = None) -> Callable:
    """Wrap add-on end function into Addon object."""

    def wrapper(func: Callable[[VoiceAssistant], None]) -> Addon:
        return Addon(func, core_attr, at_start=False, name=name)

    return wrapper


__all__ = ["Addon", "addon_begin", "addon_end"]
