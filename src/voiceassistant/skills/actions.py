"""Host built-in actions."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, List, Union

from voiceassistant.skills.create import action

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


@action("say")
def say(vass: VoiceAssistant, text: Union[str, List[str]]) -> None:
    """Say a text or randamly chosen text."""
    if isinstance(text, str):
        vass.interfaces.speech.output(text)
    elif isinstance(text, list):
        vass.interfaces.speech.output(random.choice(text))
