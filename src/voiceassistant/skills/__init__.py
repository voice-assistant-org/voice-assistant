"""Voice Assistant skills subpackage."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Dict, List, Optional

from voiceassistant.exceptions import SkillError
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict
from voiceassistant.utils.log import get_logger

from .create import Action, Skill

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)


class SkillsComponent:
    """Skills component."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize skills component."""
        self._vass = vass

        self._actions: Dict[str, Action] = {}
        self._skills: Dict[str, Skill] = {}

    @property
    def names(self) -> List[str]:
        """Get skill names."""
        return list(self._skills.keys())

    def add(self, skill: Skill) -> None:
        """Add skill."""
        if skill.name in self._skills:
            _LOGGER.warning(f"Overwriting skill {skill.name}")

        self._skills[skill.name] = skill
        _LOGGER.info(f"Skill added: {skill.name}")

    def add_action(self, action: Action, domain: Optional[str] = None) -> None:
        """Add action."""
        name = f"{domain}.{action.name}" if domain else action.name

        if name in self._actions:
            _LOGGER.warning(f"Overwriting action {name}")

        self._actions[name] = action
        _LOGGER.info(f"Action added: {name}")

    def make_from_actions(
        self, name: str, actions: List[DottedDict], variables: Optional[DottedDict]
    ) -> Skill:
        """Make a Skill object from `actions` specified in config."""

        def skill_func(entities: DottedDict, interface: InterfaceIO) -> None:
            for action_data in copy.deepcopy(actions):
                action = self._actions[action_data.pop("name")]

                action.run(vass=self._vass, entities=entities, interface=interface, **action_data)

        return Skill(name, skill_func)

    def run(self, name: str, entities: DottedDict, interface: InterfaceIO) -> None:
        """Execute skill by `name`."""
        try:
            skill = self._skills[name]
        except KeyError as e:
            raise SkillError(f"Skill {e} does not exist")

        skill.run(self._vass, entities, interface)


__all__ = ["SkillsComponent"]
