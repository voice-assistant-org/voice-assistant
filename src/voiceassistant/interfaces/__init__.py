"""Voice Assistant interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .http import HttpInterface
from .speech import SpeechInterface

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant


class InterfacesComponent:
    """Voice Assistant Interface Component."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Initialize interfaces."""
        self.speech = SpeechInterface(vass)
        self.http = HttpInterface(vass)

        vass.add_job(self.speech.run)
        vass.add_job(self.http.run)


__all__ = ["InterfacesComponent"]
