"""Host Voice Assistant Integrations component."""

from __future__ import annotations

import importlib
import inspect
from typing import TYPE_CHECKING, Any, Callable, List, Type

from voiceassistant.config import Config

from .base import Integration

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


_PACKAGE = "voiceassistant.integrations"
_INTEGRATION_MODULES = ["hass"]


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

            print(f"Importing integration: {module_name}")
            module = importlib.import_module(f".{module_name}", _PACKAGE)
            integration_classes = inspect.getmembers(
                module, _is_subclass_of(Integration),
            )
            integrations.extend(
                class_[1](self._vass) for class_ in integration_classes
            )

        for integration in integrations:
            if integration.actions:
                for action in integration.actions:
                    self._vass.skills.add_action(
                        action, domain=integration.name
                    )

            if integration.skills:
                for skill in integration.skills:
                    self._vass.skills.add(skill)

            if integration.regex_intents:
                for intent in integration.regex_intents:
                    self._vass.nlp.regex.add(**intent)


def _is_subclass_of(base_type: Type) -> Callable[[Any], bool]:
    """Get a function that determines if `obj` is subclass of `base_type`."""

    def is_subclass(obj: Any) -> bool:
        return (
            inspect.isclass(obj)
            and issubclass(obj, base_type)
            and obj is not base_type
        )

    return is_subclass


__all__ = ["IntegrationsComponent"]