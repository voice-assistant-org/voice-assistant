"""Voice Assistant skills subpackage."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Dict, List, Optional

from voiceassistant.config import Config
from voiceassistant.exceptions import SkillError
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict
from voiceassistant.utils.log import get_logger

from . import actions, skills
from .create import Action, Skill, skill

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)

# skills defined in this subpackage
_INTERNAL_SKILLS = [
    skills.weather,
    skills.current_time,
    skills.reload,
]


_INTERNAL_ACTIONS = [
    actions.say,
]


class SkillsComponent:
    """Skills component."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize skills component."""
        self._vass = vass

        self._actions: Dict[str, Action] = {}
        self._skills: Dict[str, Skill] = {}

        for skill_ in _INTERNAL_SKILLS:
            self.add(skill_)

        for action in _INTERNAL_ACTIONS:
            self.add_action(action)

        self.load_config_skills()

    @property
    def names(self) -> List[str]:
        """Get skill names."""
        return list(self._skills.keys())

    def load_config_skills(self) -> None:
        """Load skills specified in configuration.yaml."""
        for skill_spec in Config.get("skills", []):
            skill = self._make_from_config(
                name=skill_spec["name"],
                actions=skill_spec["actions"],
                variables=skill_spec.get("variables"),
            )
            self.add(skill)

    def add(self, skill: Skill) -> None:
        """Add skill."""
        if skill.name in self._skills:
            _LOGGER.warning(f"Overwriting skill {skill.name}")

        self._skills[skill.name] = skill
        _LOGGER.info(f"Skill added: {skill.name}")

    def _make_from_config(
        self, name: str, actions: List[DottedDict], variables: Optional[DottedDict]
    ) -> Skill:
        """Make skill function from `actions` specified in config."""

        @skill(name)
        def new_skill(entities: DottedDict, interface: InterfaceIO) -> None:
            for action_data in copy.deepcopy(actions):
                action = self._actions[action_data.pop("name")]

                action.run(vass=self._vass, entities=entities, interface=interface, **action_data)

        return new_skill  # type: ignore

    def add_action(self, action: Action, domain: Optional[str] = None) -> None:
        """Add action."""
        name = f"{domain}.{action.name}" if domain else action.name

        if name in self._actions:
            _LOGGER.warning(f"Overwriting action {name}")

        self._actions[name] = action
        _LOGGER.info(f"Action added: {name}")

    def run(self, name: str, entities: DottedDict, interface: InterfaceIO) -> None:
        """Execute skill by `name`."""
        try:
            self._skills[name].run(self._vass, entities, interface)
        except KeyError as e:
            raise SkillError(f"Skill {e} does not exist")


__all__ = ["SkillsComponent"]
