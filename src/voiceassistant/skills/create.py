"""Host abstract skill class."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from voiceassistant.exceptions import ActionError, SkillError
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict
from voiceassistant.utils.log import get_logger

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)


@dataclass
class Routine:
    """Base routine class."""

    name: str
    func: Callable

    def __post_init__(self) -> None:
        """Post init."""
        self._args = inspect.signature(self.func).parameters


class Skill(Routine):
    """Skill class."""

    def run(self, vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
        """Call skill function with arguments that it accepts."""
        possible_kwargs = {
            "vass": vass,
            "entities": entities,
            "interface": interface,
        }
        try:
            kwargs = {arg: possible_kwargs[arg] for arg in self._args}
        except KeyError as e:
            raise SkillError(f"Skill function {self.name} has unrecognized argument: {e}")

        to_print = "\n".join((f"name:     {self.name}", f"entities: {entities}"))
        _LOGGER.info(f"Intent recognized\n\033[92m{to_print}\033[0m")

        self.func(**kwargs)


class Action(Routine):
    """Action class."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.3, min=0.3, max=1),
        retry=retry_if_not_exception_type(ActionError),
        reraise=True,
    )
    def run(
        self, vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO, **kwargs: Any
    ) -> None:
        """Call action function with arguments that it accepts."""
        possible_kwargs = {
            "vass": vass,
            "entities": entities,
            "interface": interface,
            **kwargs,
        }
        kwargs = {arg: possible_kwargs[arg] for arg in self._args if arg in possible_kwargs}
        try:
            self.func(**kwargs)
        except TypeError as e:
            raise ActionError(e)


def skill(name: str) -> Callable:
    """Wrap function to transform it into Skill object."""

    def wrapper(func: Callable) -> Skill:
        return Skill(name, func)

    return wrapper


def action(name: str) -> Callable:
    """Wrap function to transform it into Action object."""

    def wrapper(func: Callable) -> Action:
        return Action(name, func)

    return wrapper


__all__ = ["Action", "Skill", "action", "skill"]
