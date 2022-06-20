"""Host Base Integration class."""

import abc
from typing import List

from voiceassistant.addons.create import Addon
from voiceassistant.nlp.regex import RegexIntent
from voiceassistant.skills.create import Action, Skill


class Integration(abc.ABC):
    """Base integration class that sets required properties."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return integration name."""
        raise NotImplementedError

    @property
    def actions(self) -> List[Action]:
        """Return list of actions implemented by integration."""
        return []

    @property
    def skills(self) -> List[Skill]:
        """Return list of skills implemented by integration."""
        return []

    @property
    def addons(self) -> List[Addon]:
        """Return list of regex intents implemented by integration."""
        return []

    @property
    def regex_intents(self) -> List[RegexIntent]:
        """Return list of regex intents implemented by integration."""
        return []
