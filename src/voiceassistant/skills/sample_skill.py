"""Sample voice assistant skills."""


from datetime import datetime

from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.datastruct import DottedDict

from .create import skill


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
