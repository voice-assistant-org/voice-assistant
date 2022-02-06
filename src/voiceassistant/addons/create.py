"""Host add-on creation tools."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

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


@dataclass
class Addon:
    """Voice Assistant Add-on representation."""

    func: Callable[[VoiceAssistant], None]
    core_attr: CoreAttribute
    at_start: bool
    name_: Optional[str] = None

    @property
    def name(self) -> str:
        """Return addon name."""
        return self.name_ or self.func.__name__  # type: ignore


def addon_begin(core_attr: CoreAttribute, name: Optional[str] = None) -> Callable:
    """Wrap add-on begin function into Addon object."""

    def wrapper(func: Callable[[VoiceAssistant], None]) -> Addon:
        return Addon(func, core_attr, at_start=True, name_=name)

    return wrapper


def addon_end(core_attr: CoreAttribute, name: Optional[str] = None) -> Callable:
    """Wrap add-on end function into Addon object."""

    def wrapper(func: Callable[[VoiceAssistant], None]) -> Addon:
        return Addon(func, core_attr, at_start=False, name_=name)

    return wrapper


__all__ = ["Addon", "addon_begin", "addon_end"]
