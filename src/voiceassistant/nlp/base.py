"""Voice Assistant base NL processor."""

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Callable, Optional

from voiceassistant.utils.datastruct import DottedDict

if TYPE_CHECKING:
    from voiceassistant.interfaces.base import InterfaceIO


@dataclass
class NlpResult:
    """NLP Result class.

    Should be a return type of all NL processors.
    """

    skill_name: str
    skill_func: Callable
    entities: DottedDict
    is_complete: bool

    def __str__(self) -> str:
        """Get string representation of an instance."""
        return "\n".join(f"{k}: {v}" for k, v in asdict(self).items())

    def execute_skill(self, interface: "InterfaceIO") -> None:
        """Execute skill function from NLP result."""
        print(f"\033[92m{self}\033[0m")
        self.skill_func(entities=self.entities, interface=interface)


class BaseNLP(ABC):
    """Base Natural Language Processor."""

    @abstractmethod
    def process(self, transcript: str) -> Optional[NlpResult]:
        """Process natural language `transcript`."""
        pass
