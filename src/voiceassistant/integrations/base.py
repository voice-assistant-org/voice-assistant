"""Host Base Integration class."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Dict, List

from voiceassistant.skills.base import Action, Skill

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


class Integration(abc.ABC):
    """Base integration class that sets required properties."""

    @abc.abstractmethod
    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return integration name."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def actions(self) -> List[Action]:
        """Return list of actions implemented by integration."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def skills(self) -> List[Skill]:
        """Return list of skills implemented by integration."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def regex_intents(self) -> List[Dict]:
        """Return list of regex intents implemented by integration."""
        raise NotImplementedError
