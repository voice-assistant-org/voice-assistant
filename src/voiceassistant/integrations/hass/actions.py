"""Home assistant actions."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.skills.create import action

from .const import CLIENT, DOMAIN

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


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


ACTIONS = [
    say_from_template,
    call_service,
    fire_event,
    set_state,
    run_script,
]
