"""Home assistant skills."""

from __future__ import annotations

from typing import TYPE_CHECKING

from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict

from .const import CLIENT, DOMAIN, NAME_TO_ENTITY, ColorMode
from .utils import hass_skill, re_number_range, re_separate_word, word_or_str_to_int

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


COVER_MAX_POS = 5
LIGHT_MAX_BRIGHTNESS = 9


RE_TURN_ON = re_separate_word("on") + "|enable|start"
RE_TURN_OFF = re_separate_word("off") + "|disable|stop"
RE_DIM_LIGHT = re_separate_word("dim")
RE_BRIGHTEN_LIGHT = "brighten"
BRIGHTNESS_FACTOR = 100

RE_LIGHT_BRIGHTNESS = re_number_range(0, LIGHT_MAX_BRIGHTNESS)


RE_OPEN_COVER = re_separate_word("up") + "|open"
RE_CLOSE_COVER = "down|close"
RE_COVER_POSITION = re_number_range(0, COVER_MAX_POS)


@hass_skill(
    name="hass-turn-on",
    hass_entity_filters={"service": "turn_on"},
    skill_regex=RE_TURN_ON,
)
def turn_on(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Turn on HASS entity."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].turn_on(entity_id)
    interface.output(f"{entities.hass_entity_name}'s on")


@hass_skill(
    name="hass-turn-off",
    hass_entity_filters={"service": "turn_off"},
    skill_regex=RE_TURN_OFF,
)
def turn_off(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Turn off HASS entity."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].turn_off(entity_id)
    interface.output(f"{entities.hass_entity_name}'s off")


@hass_skill(
    name="hass-dim-light",
    hass_entity_filters={
        "domains": {"light"},
        "attributes": {
            "supported_color_modes": {
                ColorMode.BRIGHTNESS,
                ColorMode.COLOR_TEMP,
                ColorMode.HS,
                ColorMode.XY,
                ColorMode.RGB,
                ColorMode.RGBW,
                ColorMode.RGBWW,
                ColorMode.WHITE,
            }
        },
    },
    skill_regex=RE_DIM_LIGHT,
)
def dim_light(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Set brightness skill."""
    client = vass.data[DOMAIN][CLIENT]
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        brightness = client.get_state(entity_id).attributes.get("brightness", 0)
        brightness -= BRIGHTNESS_FACTOR

        if brightness <= 0:
            client.turn_off(entity_id)
        else:
            data = {"brightness": brightness}
            client.call_service("turn_on", entity_id, **data)


@hass_skill(
    name="hass-brighten-light",
    hass_entity_filters={
        "domains": {"light"},
        "attributes": {
            "supported_color_modes": {
                ColorMode.BRIGHTNESS,
                ColorMode.COLOR_TEMP,
                ColorMode.HS,
                ColorMode.XY,
                ColorMode.RGB,
                ColorMode.RGBW,
                ColorMode.RGBWW,
                ColorMode.WHITE,
            }
        },
    },
    skill_regex=RE_BRIGHTEN_LIGHT,
)
def brighten_light(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Set brightness skill."""
    client = vass.data[DOMAIN][CLIENT]
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        brightness = client.get_state(entity_id).attributes.get("brightness", 0)
        brightness += BRIGHTNESS_FACTOR

        if brightness > 255:
            brightness = 255

        data = {"brightness": brightness}
        client.call_service("turn_on", entity_id, **data)


@hass_skill(
    name="hass-set-brightness",
    hass_entity_filters={
        "domains": {"light"},
        "attributes": {
            "supported_color_modes": {
                ColorMode.BRIGHTNESS,
                ColorMode.COLOR_TEMP,
                ColorMode.HS,
                ColorMode.XY,
                ColorMode.RGB,
                ColorMode.RGBW,
                ColorMode.RGBWW,
                ColorMode.WHITE,
            }
        },
    },
    skill_regex=RE_LIGHT_BRIGHTNESS,
    nlp_entities={"brightness": [RE_LIGHT_BRIGHTNESS]},
)
def set_brightness(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Set brightness skill."""
    client = vass.data[DOMAIN][CLIENT]
    brightness = int(word_or_str_to_int(entities.brightness) * 255 / LIGHT_MAX_BRIGHTNESS)
    data = {"brightness": brightness}
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        client.call_service("turn_on", entity_id, **data)


@hass_skill(
    name="hass-open-cover",
    hass_entity_filters={"domains": {"cover"}},
    skill_regex=RE_OPEN_COVER,
)
def open_cover(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Call open_cover service for HASS cover entity e.g. blinds."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].open_cover(entity_id)
    interface.output(f"opening {entities.hass_entity_name}")


@hass_skill(
    name="hass-close-cover",
    hass_entity_filters={"domains": {"cover"}},
    skill_regex=RE_CLOSE_COVER,
)
def close_cover(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Call open_cover service for HASS cover entity e.g. blinds."""
    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        vass.data[DOMAIN][CLIENT].close_cover(entity_id)
    interface.output(f"closing {entities.hass_entity_name}")


@hass_skill(
    name="hass-set-cover-position",
    hass_entity_filters={"domains": {"cover"}},
    skill_regex=RE_COVER_POSITION,
    nlp_entities={"position": [RE_COVER_POSITION]},
)
def set_cover_position(vass: VoiceAssistant, entities: DottedDict, interface: InterfaceIO) -> None:
    """Set cover position."""
    client = vass.data[DOMAIN][CLIENT]
    position = word_or_str_to_int(entities.position) * 100 / COVER_MAX_POS

    for entity_id in vass.data[DOMAIN][NAME_TO_ENTITY][entities.hass_entity_name]:
        client.set_cover_position(entity_id, position)


SKILLS = [
    turn_on,
    turn_off,
    dim_light,
    brighten_light,
    set_brightness,
    open_cover,
    close_cover,
    set_cover_position,
]
