"""NLP Result class.

Should be a return type of all NL processors.
"""
from typing import TYPE_CHECKING, Any, Callable, Tuple

from voiceassistant.utils.datastruct import DottedDict

if TYPE_CHECKING:
    from voiceassistant.interfaces.base import InterfaceIO


class NlpResult:
    """NLP Result class."""

    def __init__(
        self,
        skill_name: str,
        skill_func: Callable,
        entities: DottedDict,
        is_complete: bool,
    ):
        """Init."""
        self.skill_name = skill_name
        self.skill_func = skill_func
        self.entities = entities
        self.is_complete = is_complete

    def __str__(self) -> str:
        """Get string respesentation of NLP result."""
        return "\n".join(
            (
                "_" * 20,
                "NLP Result:",
                f"skill:    {self.skill_name}",
                f"entities: {self.entities}",
                f"complete: {self.is_complete}",
                "_" * 20,
            )
        )

    def _key(self) -> Tuple:
        """Get NLP result key."""
        return (
            tuple((k, v) for k, v in self.entities.items()),
            self.skill_func,
            self.is_complete,
        )

    def __hash__(self) -> int:
        """Get hash of this object."""
        return hash(self._key())

    def __eq__(self, other: Any) -> bool:
        """Check equality with another NlpResult instance."""
        return self._key() == other._key()  # type: ignore

    def execute_skill(self, interface: "InterfaceIO") -> None:
        """Execute skill function from NLP result."""
        print(self)
        self.skill_func(entities=self.entities, interface=interface)
