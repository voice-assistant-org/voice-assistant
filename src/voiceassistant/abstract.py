"""Host an abstract representation of a core Voice Assistant component."""

from __future__ import annotations

import abc

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import VoiceAssistant


class CoreComponent(abc.ABC):
    """Core component abstract class."""

    @abc.abstractmethod
    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize component."""
        raise NotImplementedError

    @abc.abstractmethod
    def reload(self) -> None:
        """Reload component."""
        raise NotImplementedError
