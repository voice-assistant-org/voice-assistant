"""Host Voice Assistant Integrations component."""

from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING, Any, Callable, List, Type

from voiceassistant.config import Config
from voiceassistant.exceptions import IntegrationError
from voiceassistant.utils.log import get_logger

from .base import Integration

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)

_PACKAGE = "voiceassistant.integrations"
_INTEGRATION_MODULES = ["respeaker", "hass", "spotify"]


class IntegrationsComponent:
    """Integrations component."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize and load integraions."""
        self._vass = vass
        self.load_integrations()

    def load_integrations(self) -> None:
        """Load enabled integrations."""
        integrations: List[Integration] = []

        for module_name in _INTEGRATION_MODULES:
            if module_name not in Config:
                continue

            _LOGGER.info(f"Importing integration: {module_name}")
            try:
                module = importlib.import_module(f".{module_name}", _PACKAGE)
                integration_classes = inspect.getmembers(module, _is_subclass_of(Integration))
                integrations.extend(class_[1](self._vass) for class_ in integration_classes)
            except IntegrationError as e:
                _LOGGER.error(f"Unable to import integration '{module_name}': {e}")
            except Exception:
                _LOGGER.exception(
                    f"Unexpected exception while importing integration '{module_name}'"
                )

        for integration in integrations:

            actions = integration.actions
            if actions:
                for action in actions:
                    self._vass.skills.add_action(action, domain=integration.name)

            skills = integration.skills
            if skills:
                for skill in skills:
                    self._vass.skills.add(skill)

            regex_intents = integration.regex_intents
            if regex_intents:
                for intent in regex_intents:
                    self._vass.nlp.regex.add(**intent)

            addons = integration.addons
            if addons:
                for addon in addons:
                    self._vass.addons.add(addon)


def _is_subclass_of(base_type: Type) -> Callable[[Any], bool]:
    """Get a function that determines if `obj` is subclass of `base_type`."""

    def is_subclass(obj: Any) -> bool:
        return inspect.isclass(obj) and issubclass(obj, base_type) and obj is not base_type

    return is_subclass


__all__ = ["IntegrationsComponent"]
