"""Add-On functions for speech interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from voiceassistant.addons.create import Addon, CoreAttribute, addon_begin, addon_end
from voiceassistant.exceptions import IntegrationError
from voiceassistant.utils.log import get_logger

from .base import Integration

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)

try:
    from pixel_ring import apa102_pixel_ring, pixel_ring

    if isinstance(pixel_ring, apa102_pixel_ring.PixelRing):
        _LOGGER.info("Found ReSpeaker 4 Mic Array")

        from gpiozero import LED

        power = LED(5)
        power.on()
        pixel_ring.change_pattern("echo")

    class PixelRingState:
        """Host pixel ring states."""

        off = 0
        speak = 1
        think = 2

    pixel_ring.off()
    ring_state = PixelRingState.off

except Exception as e:
    raise IntegrationError(f"No ReSpeaker Microphone detected or not able to connect: {e}") from e


class RespeakerMicrophoneArray(Integration):
    """Respeaker Microphone Array integration."""

    name = "respeaker"

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        pass

    @property
    def addons(self) -> List[Addon]:
        """Get addons."""
        return [processing_starts, processing_ends, tts_starts, tts_ends]


@addon_begin(CoreAttribute.SPEECH_PROCESSING)
def processing_starts(vass: VoiceAssistant) -> None:
    """Do before NLP starts."""
    pixel_ring.speak()
    global ring_state
    ring_state = PixelRingState.speak


@addon_end(CoreAttribute.SPEECH_PROCESSING)
def processing_ends(vass: VoiceAssistant) -> None:
    """Do when NLP ends."""
    pixel_ring.off()
    global ring_state
    ring_state = PixelRingState.off


@addon_begin(CoreAttribute.SPEECH_OUTPUT)
def tts_starts(vass: VoiceAssistant) -> None:
    """Do before voice output starts."""
    pixel_ring.think()


@addon_end(CoreAttribute.SPEECH_OUTPUT)
def tts_ends(vass: VoiceAssistant) -> None:
    """Do when voice output ends."""
    if ring_state == PixelRingState.speak:
        pixel_ring.speak()
    else:
        pixel_ring.off()
