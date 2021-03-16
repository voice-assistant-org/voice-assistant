"""Current time skill."""

from datetime import datetime

from src.interfaces import InterfaceType
from src.nlp.regex import regex_skill
from src.utils.datastruct import DottedDict


@regex_skill(
    expressions=("what's the time", "what time is it",),
    entities={"location": ("Moscow", "London")},
)
def get_time(entities: DottedDict, interface: InterfaceType) -> None:
    """Get current time."""
    time_now = datetime.now().strftime("%H:%M")
    interface.output(f"It's {time_now}")


@regex_skill(expressions=("weather",),)
def get_weather(entities: DottedDict, interface: InterfaceType) -> None:
    """Get weather."""
    interface.output("weather is nice")


@regex_skill(expressions=("google for <<request>>",),)
def google_for(entities: DottedDict, interface: InterfaceType) -> None:
    """Google for somthing."""
    print(entities.request)
