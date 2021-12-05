"""Sample voice assistant skills."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import yaml

from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict

from .create import skill

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


@skill("weather")
def weather(entities: DottedDict, interface: InterfaceIO) -> None:
    """Get weather sample skill."""
    if entities.get("city"):
        interface.output(f"weather in {entities.city} is nice")
    else:
        interface.output("weather is nice")


@skill("current-time")
def current_time(interface: InterfaceIO) -> None:
    """Get current time."""
    time_now = datetime.now().strftime("%H:%M")
    interface.output(f"It's {time_now}")


@skill("reload")
def reload(vass: VoiceAssistant, interface: InterfaceIO) -> None:
    """Reload Voice Assistant."""
    try:
        vass.load_components()
        interface.output("I am now reloaded")
    except yaml.scanner.ScannerError:
        interface.output("Aborting, configuration YAML file is invalid.")
