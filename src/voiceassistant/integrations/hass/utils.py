"""Home assistant integration utils."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Set

from voiceassistant.nlp.regex import RegexIntent
from voiceassistant.skills.create import Skill

from .const import CLIENT, DOMAIN, SERVICES

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

WORD_TO_INT = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def re_separate_word(word: str) -> str:
    """Conver word to regex considering word's position in a sentence."""
    return f" {word}$|^{word} | {word} "


def word_or_str_to_int(word: str) -> int:
    """Convert word to number."""
    try:
        return int(float(word))
    except ValueError:
        pass

    try:
        return WORD_TO_INT[word.strip()]
    except KeyError:
        raise ValueError(f"Can't convert to int: {word}")


def re_number_range(minimum: int, maximum: int) -> str:
    """Get regex to match integer in range."""
    assert maximum < 10, "above 10 is not supported"
    return "{numeric}|{wordic}".format(
        numeric=re_separate_word(f"[{minimum}-{maximum}]"),
        wordic="|".join(list(WORD_TO_INT.keys())[minimum : maximum + 1]),
    )


@dataclass
class HassSkill(Skill):
    """HASS skill representation."""

    hass_entity_filters: Dict[str, Any]
    skill_regex: str
    nlp_entities: Dict[str, List[str]] | None

    def get_intent(self, vass: VoiceAssistant) -> RegexIntent:
        """Get regex intent object for this skill."""
        friendly_names = get_friendly_names_with_filter(
            vass=vass,
            domains=self.hass_entity_filters.get("domains"),
            service=self.hass_entity_filters.get("service"),
            attributes=self.hass_entity_filters.get("attributes"),
        )
        re_names = "|".join(friendly_names)
        expressions = (f"({self.skill_regex}&&{re_names})",)
        entities = {"hass_entity_name": friendly_names}

        if self.nlp_entities:
            entities.update(self.nlp_entities)

        return RegexIntent(name=self.name, expressions=expressions, entities=entities)


def hass_skill(
    name: str,
    hass_entity_filters: Dict[str, Any],
    skill_regex: str,
    nlp_entities: Dict[str, List[str]] | None = None,
) -> Callable:
    """Wrap function to convert it to HassSkill."""

    def wrapper(func: Callable) -> HassSkill:
        return HassSkill(name, func, hass_entity_filters, skill_regex, nlp_entities)

    return wrapper


def get_friendly_names_with_filter(
    vass: VoiceAssistant,
    domains: Set[str] | None = None,
    service: str | None = None,
    attributes: Dict[str, Any] | None = None,
) -> List[str]:
    """Get friendly names of entities from config for which condition satisfies."""
    result = set()
    for item in vass.config.hass.entities:
        for entity_id in item.ids:
            if not irrelevant(vass, entity_id, domains, service, attributes):
                result |= set(item.names)

    return list(result)


def irrelevant(
    vass: VoiceAssistant,
    entity_id: str,
    domains: Set[str] | None = None,
    service: str | None = None,
    attributes: Dict[str, Any] | None = None,
) -> bool:
    """Check if entity does not satisfy filtering criteria."""
    client = vass.data[DOMAIN][CLIENT]
    hass_services = vass.data[DOMAIN][SERVICES]

    if domains and service:
        raise TypeError("Can't pass both domains and service")

    if domains and domain(entity_id) not in domains:
        return True

    if service:
        domains_with_service = {item.domain for item in hass_services if service in item.services}
        if domain(entity_id) not in domains_with_service:
            return True

    if attributes:
        entity_attributes = client.get_state(entity_id).attributes
        for key, value in attributes.items():
            attr = entity_attributes.get(key)
            if isinstance(attr, list):
                attr = set(attr)
            elif isinstance(attr, str):
                attr = {attr}
            else:
                raise TypeError(f"Hass attribute {key} of type {type(attr)} is not expected.")

            # if sets do not intersect
            if not (attr & value):
                return True

    return False


def domain(entity_id: str) -> str:
    """Get domain from entity id."""
    return entity_id.split(".")[0]
