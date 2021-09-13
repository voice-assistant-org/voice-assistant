"""Voice Assistant base NL processor."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from voiceassistant.utils.datastruct import DottedDict


@dataclass
class NlpResult:
    """NLP Result class.

    Should be a return type of all NL processors.
    """

    intent: str
    entities: DottedDict
    is_complete: bool


class BaseNLP(ABC):
    """Base Natural Language Processor."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return NL Processor name."""
        raise NotImplementedError

    @abstractmethod
    def process(self, transcript: str) -> Optional[NlpResult]:
        """Process natural language `transcript`."""
        raise NotImplementedError
