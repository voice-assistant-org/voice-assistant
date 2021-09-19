"""Host abstract skill class."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from voiceassistant.exceptions import ActionError, SkillError
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


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

    def run(self, vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO,) -> None:
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
        print(f"\n\033[92m{to_print}\033[0m")

        self.func(**kwargs)


class Action(Routine):
    """Action class."""

    def run(
        self, vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO, **kwargs: Any,
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
