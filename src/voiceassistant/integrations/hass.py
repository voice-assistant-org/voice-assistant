"""Host Home Assistant integration."""

from __future__ import annotations

import random
from collections import namedtuple
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from hassapi import Hass
from hassapi.exceptions import ClientError, Unauthorised

from voiceassistant.exceptions import IntegrationError
from voiceassistant.integrations.base import Integration
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.nlp.regex import RegexIntent
from voiceassistant.skills.create import Action, Skill, action, skill
from voiceassistant.utils.datastruct import DottedDict

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.config import Config


DOMAIN = "hass"

CLIENT = "client"
NAME_TO_ENTITY = "name_to_entity"


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

    return HomeAssistant(vass)


class HomeAssistant(Integration):
    """Home Assistant integration."""

    name = DOMAIN

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        self._vass = vass

    @property
    def actions(self) -> List[Action]:
        """Return list of hass-actions."""
        return [
            say_from_template,
            call_service,
            fire_event,
            set_state,
            run_script,
        ]

    @property
    def skills(self) -> List[Skill]:
        """Return list of hass-skills."""
        return [
            turn_on,
            turn_off,
            open_cover,
            close_cover,
        ]

    @property
    def regex_intents(self) -> List[RegexIntent]:
        """Return list of hass-regex-intents."""
        Intent = namedtuple("Intent", "name, service, regex")
        intents = (
            Intent("hass-turn-on", "turn_on", " on|enable|start"),
            Intent("hass-turn-off", "turn_off", " off|disable"),
            Intent("hass-open-cover", "open_cover", " up|open"),
            Intent("hass-close-cover", "close_cover", "down|close"),
        )
        result: List[RegexIntent] = []
        for intent in intents:
            entity_names = _get_names_with_service(intent.service, self._vass)
            entity_names_regex = "|".join(entity_names)
            result.append(
                RegexIntent(
                    name=intent.name,
                    expressions=(f"({intent.regex}&&{entity_names_regex})",),
                    entities={"hass_entity_name": entity_names},
                )
            )
        return result


@action("say_from_template")
def say_from_template(
    vass: VoiceAssistant, interface: InterfaceIO, template: Union[str, List[str]]
) -> None:
    """Render HASS Jinja2 template and output result via `interface`."""
    if isinstance(template, str):
        interface.output(vass.data[DOMAIN][CLIENT].render_template(template))
    elif isinstance(template, list):
        interface.output(vass.data[DOMAIN][CLIENT].render_template(random.choice(template)))


@action("call_service")
def call_service(
    vass: VoiceAssistant, service: str, entity_id: str, data: Optional[Dict] = None
) -> None:
    """Call HASS service."""
    data = data or {}
    vass.data[DOMAIN][CLIENT].call_service(service, entity_id, **data)


@action("fire_event")
def fire_event(vass: VoiceAssistant, event_type: str, event_data: Dict) -> None:
    """Fire HASS event."""
    vass.data[DOMAIN][CLIENT].fire_event(event_type, event_data)


@action("set_state")
def set_state(vass: VoiceAssistant, entity_id: str, state: str) -> None:
    """Set state of a HASS entity."""
    vass.data[DOMAIN][CLIENT].set_state(entity_id, state)


@action("run_script")
def run_script(vass: VoiceAssistant, script_id: str) -> None:
    """Run HASS script."""
    vass.data[DOMAIN][CLIENT].run_script(script_id)


@skill("hass-turn-on")
def turn_on(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Turn on HASS entity."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].turn_on(entity_id)
    interface.output(f"turning on the {entities.hass_entity_name}")


@skill("hass-turn-off")
def turn_off(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Turn off HASS entity."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].turn_off(entity_id)
    interface.output(f"turning off the {entities.hass_entity_name}")


@skill("hass-open-cover")
def open_cover(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Call open_cover service for HASS cover entity e.g. blinds."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].open_cover(entity_id)
    interface.output(f"opening {entities.hass_entity_name}")


@skill("hass-close-cover")
def close_cover(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Call close_cover service for HASS cover entity e.g. blinds."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].close_cover(entity_id)
    interface.output(f"closing {entities.hass_entity_name}")


def _get_names_with_service(service: str, vass: VoiceAssistant) -> List[str]:
    """Get names of entities from Config for which `service` is applicable.

    Args:
        service: HASS service name e.g. turn_on
    Returns:
        entity friendly names for which `service` is applicable e.g.
            'turn_on' can be applicable for "bedroom lights"
    """
    domains = [
        item.domain
        for item in vass.data[DOMAIN][CLIENT].get_services()
        if service in item.services
    ]

    result = []
    for ent in vass.config.hass.entities:
        for ent_id in ent.ids:
            domain = ent_id.split(".")[0]
            if domain in domains:
                result.extend(ent.names)

    return result


__all__ = ["HomeAssistant"]
