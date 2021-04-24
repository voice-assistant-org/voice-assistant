"""Home assistant control configurable skill."""

import hassapi

from voiceassistant.interfaces import InterfaceType
from voiceassistant.nlp.regex import regex_skill
from voiceassistant.utils.config import Config
from voiceassistant.utils.datastruct import DottedDict
from voiceassistant.utils.hass import (
    get_entity_ids,
    hass_regex_skill,
    make_skill_func,
)

hass = hassapi.Hass(
    hassurl=Config.hass.url, token=Config.hass.token, timeout=20
)


@hass_regex_skill("turn_on", keywords=("on", "enable", "start"), hass=hass)
def turn_on(entities: DottedDict, interface: InterfaceType) -> None:
    """Turn on HASS entity."""
    for entity_id in get_entity_ids(entities.hass_entity_name):
        hass.turn_on(entity_id)
    interface.output(f"turning on the {entities.hass_entity_name}")


@hass_regex_skill("turn_off", keywords=("off", "disable"), hass=hass)
def turn_off(entities: DottedDict, interface: InterfaceType) -> None:
    """Turn off HASS entity."""
    for entity_id in get_entity_ids(entities.hass_entity_name):
        hass.turn_off(entity_id)
    interface.output(f"turning off the {entities.hass_entity_name}")


@hass_regex_skill("open_cover", keywords=("up", "open"), hass=hass)
def open_cover(entities: DottedDict, interface: InterfaceType) -> None:
    """Call open_cover service for HASS cover entity e.g. blinds."""
    for entity_id in get_entity_ids(entities.hass_entity_name):
        hass.open_cover(entity_id)
    interface.output(f"opening {entities.hass_entity_name}")


@hass_regex_skill("close_cover", keywords=("down", "close"), hass=hass)
def close_cover(entities: DottedDict, interface: InterfaceType) -> None:
    """Call close_cover service for HASS cover entity e.g. blinds."""
    for entity_id in get_entity_ids(entities.hass_entity_name):
        hass.close_cover(entity_id)
    interface.output(f"closing {entities.hass_entity_name}")


def _register_hass_custom_skills(hass: hassapi.Hass) -> None:
    """Register HASS custom skills specified in Config.hass.skills."""
    for skill in Config.hass.skills:
        # register skill
        regex_skill(expressions=skill.expressions)(
            make_skill_func(skill.actions, hass)
        )


_register_hass_custom_skills(hass)
