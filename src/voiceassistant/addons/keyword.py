"""Add-On functions for triggerword detection event."""

import random

from voiceassistant.config import Config
from voiceassistant.exceptions import DottedAttribureError


def react_to_keyword(vass) -> None:  # type: ignore
    """React to trigger word."""
    try:
        vass.speech.output(
            text=random.choice(Config.triggerword.replies), cache=True,
        )
    except DottedAttribureError:
        pass
