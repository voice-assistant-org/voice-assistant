"""Current time skill."""

from datetime import datetime

from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.nlp.regex import regex_skill
from voiceassistant.utils.datastruct import DottedDict


@regex_skill(
    expressions=("(what&&time)",), entities={"location": ("Moscow", "London")},
)
def get_time(entities: DottedDict, interface: InterfaceIO) -> None:
    """Get current time."""
    time_now = datetime.now().strftime("%H:%M")
    interface.output(f"It's {time_now}")


@regex_skill(expressions=("google for <<request>>",),)
def google_for(entities: DottedDict, interface: InterfaceIO) -> None:
    """Google for somthing."""
    print(entities.request)
