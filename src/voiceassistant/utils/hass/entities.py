"""Utils for automatic creation of skills for HASS entities."""

from typing import Callable, Dict, Iterable, List, Set

import hassapi

from voiceassistant.nlp.regex import regex_skill
from voiceassistant.utils.config import Config


def hass_regex_skill(
    service: str, keywords: Iterable[str], hass: hassapi.Hass
) -> Callable:
    """Wrap regex skill for convenience."""

    def wrapper(func: Callable) -> None:
        names = _get_names_with_service(service, hass)
        names_re = "|".join(names)
        keywords_re = "|".join(keywords)
        regex_skill(
            expressions=(f"({keywords_re}&&{names_re})",),
            entities={"hass_entity_name": names},
        )(func)

    return wrapper


def get_entity_ids(name: str) -> List[str]:
    """Get HASS entity id list associated with a friendly name."""
    return _NAME_TO_IDS[name]


def _get_names_with_service(service: str, hass: hassapi.Hass) -> List[str]:
    """Get names of entities from Config for which ``service`` is applicable.

    Args:
        service: HASS service e.g. turn_on
        hass: hassapi client
    """
    domains = _get_domains_with_service(service, hass)
    names = (
        ent.names
        for ent in Config.hass.entities
        for id_ in ent.ids
        if id_.split(".")[0] in domains
    )
    return [name for sublist in names for name in sublist]  # flattened


def _get_domains_with_service(service: str, hass: hassapi.Hass) -> Set[str]:
    """Get HASS domains for which ``service`` is applicable."""
    return {
        svc.domain for svc in hass.get_services() if service in svc.services
    }


def _get_entity_name_to_ids() -> Dict[str, list]:
    """Get a mapping of name to list of HASS entity ids from Config."""
    result = {}
    for entity in Config.hass.entities:
        for name in entity.names:
            result[name] = entity.ids
    return result


_NAME_TO_IDS = _get_entity_name_to_ids()
