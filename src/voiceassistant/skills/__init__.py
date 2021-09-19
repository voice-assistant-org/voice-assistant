"""Voice Assistant skills subpackage."""

from __future__ import annotations

import copy
import warnings
from typing import TYPE_CHECKING, Dict, List, Optional

from voiceassistant.config import Config
from voiceassistant.exceptions import SkillError
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict

from . import sample_skill
from .create import Action, Skill, skill

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

# skills defined in this subpackage
_INTERNAL_SKILLS = [
    sample_skill.weather,
    sample_skill.current_time,
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

        self.load_config_skills()

    @property
    def names(self) -> List[str]:
        """Get skill names."""
        return list(self._skills.keys())

    def load_config_skills(self) -> None:
        """Load skills specified in configuration.yaml."""
        Config.reload()

        for skill_spec in Config.get("skills", []):
            self.add_from_config(skill_spec["name"], skill_spec["actions"])

    def add(self, skill: Skill) -> None:
        """Add skill."""
        if skill.name in self._skills:
            warnings.warn(f"Overwriting skill {skill.name}")

        self._skills[skill.name] = skill
        print(f"Skill added: {skill.name}")

    def add_from_config(self, name_: str, actions: List[DottedDict]) -> None:
        """Make skill function from `actions` specified in config."""

        @skill(name_)
        def new_skill(entities: DottedDict, interface: InterfaceIO) -> None:
            for action_data in copy.deepcopy(actions):
                self._actions[action_data.pop("name")].run(
                    vass=self._vass, entities=entities, interface=interface, **action_data,
                )

        self.add(new_skill)

    def add_action(self, action: Action, domain: Optional[str]) -> None:
        """Add action."""
        name = f"{domain}.{action.name}" if domain else action.name

        if name in self._actions:
            warnings.warn(f"Overwriting action {name}")

        self._actions[name] = action
        print(f"Action added: {name}")

    def run(self, name: str, entities: DottedDict, interface: InterfaceIO) -> None:
        """Execute skill by `name`."""
        try:
            self._skills[name].run(self._vass, entities, interface)
        except KeyError as e:
            raise SkillError(f"Skill {e} does not exist")


__all__ = ["SkillsComponent"]
