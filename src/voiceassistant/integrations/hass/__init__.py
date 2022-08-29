"""Home Assistant integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from hassapi import Hass
from hassapi.exceptions import ClientError, Unauthorised

from voiceassistant.exceptions import IntegrationError
from voiceassistant.integrations.base import Integration
from voiceassistant.nlp.regex import RegexIntent
from voiceassistant.skills.create import Action, Skill

from .actions import ACTIONS
from .const import CLIENT, DOMAIN, NAME_TO_ENTITY, SERVICES, STATES
from .skills import SKILLS

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.config import Config


def setup(vass: VoiceAssistant, config: Config) -> Integration:
    """Set up Home Assistant integration."""
    try:
        hass = Hass(hassurl=config.hass.url, token=config.hass.token, timeout=20)
    except ClientError:
        raise IntegrationError(
            "Unable to connect to HASS API. "
            "Make sure URL is correct and API Component is enabled."
        )
    except Unauthorised:
        raise IntegrationError("Invalid Home Assistant token")

    vass.data[DOMAIN] = {}
    vass.data[DOMAIN][CLIENT] = hass
    vass.data[DOMAIN][NAME_TO_ENTITY] = {
        name: entity.ids for entity in config.hass.entities for name in entity.names
    }
    vass.data[DOMAIN][SERVICES] = hass.get_services()
    vass.data[DOMAIN][STATES] = hass.get_states()

    integration = HomeAssistant(vass)
    # del vass.data[DOMAIN][SERVICES]
    # del vass.data[DOMAIN][STATES]

    return integration


class HomeAssistant(Integration):
    """Home Assistant integration."""

    name = DOMAIN

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        self._vass = vass

    @property
    def actions(self) -> List[Action]:
        """Return list of hass-actions."""
        return ACTIONS

    @property
    def skills(self) -> List[Skill]:
        """Return list of hass-skills."""
        return SKILLS

    @property
    def regex_intents(self) -> List[RegexIntent]:
        """Return list of hass-regex-intents."""
        return [skill.get_intent(self._vass) for skill in SKILLS]
