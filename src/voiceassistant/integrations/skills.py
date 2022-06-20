"""Host integration that allows to define custom skills."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from voiceassistant.integrations.base import Integration
from voiceassistant.nlp.regex import RegexIntent
from voiceassistant.skills.create import Skill

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.config import Config


DOMAIN = "skills"

CONF_NAME = "name"
CONF_ACTIONS = "actions"
CONF_VARIABLES = "variables"

CONF_NLP = "nlp"
CONF_EXPRESSIONS = "expressions"
CONF_ENTITIES = "entities"

REGEX = "regex"


def setup(vass: VoiceAssistant, config: Config) -> Integration:
    """Set up custom skills integraion."""
    return CustomSkills(vass, config[DOMAIN])


class CustomSkills(Integration):
    """Custom skills integration."""

    name = DOMAIN

    def __init__(self, vass: VoiceAssistant, config: Config) -> None:
        """Init."""
        self._vass = vass
        self._config = config

    @property
    def skills(self) -> List[Skill]:
        """Load skills specified in configuration.yaml."""
        return [
            self._vass.skills.make_from_actions(
                name=skill_spec[CONF_NAME],
                actions=skill_spec[CONF_ACTIONS],
                variables=skill_spec.get(CONF_VARIABLES),
            )
            for skill_spec in self._config
        ]

    @property
    def regex_intents(self) -> List[RegexIntent]:
        """Return list of regex intents implemented by integration."""
        return [
            RegexIntent(
                name=skill_spec[CONF_NAME],
                expressions=skill_spec[CONF_NLP][CONF_EXPRESSIONS],
                entities=skill_spec[CONF_NLP].get(CONF_ENTITIES),
            )
            for skill_spec in self._config
            if skill_spec[CONF_NLP][CONF_NAME] == REGEX
        ]
