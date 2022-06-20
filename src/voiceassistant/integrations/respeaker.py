"""Add-On functions for speech interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from voiceassistant.addons.create import Addon, CoreAttribute, addon_begin, addon_end
from voiceassistant.exceptions import IntegrationError
from voiceassistant.utils.log import get_logger

from .base import Integration

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant
    from voiceassistant.config import Config

try:
    from pixel_ring import apa102_pixel_ring, pixel_ring
except Exception as e:
    raise IntegrationError(f"No ReSpeaker Microphone detected or not able to connect: {e}") from e

_LOGGER = get_logger(__name__)


DOMAIN = "respeaker"
RING_STATE = "ring_state"


class PixelRingState:
    """Host pixel ring states."""

    off = 0
    speak = 1
    think = 2


def setup(vass: VoiceAssistant, config: Config) -> Integration:
    """Set up Respeaker integration."""
    if isinstance(pixel_ring, apa102_pixel_ring.PixelRing):
        _LOGGER.info("Found ReSpeaker 4 Mic Array")

        from gpiozero import LED

        power = LED(5)
        power.on()
        pixel_ring.change_pattern("echo")

    pixel_ring.off()
    vass.data[DOMAIN] = {}
    vass.data[DOMAIN][RING_STATE] = PixelRingState.off

    return RespeakerMicrophoneArray()


class RespeakerMicrophoneArray(Integration):
    """Respeaker Microphone Array integration."""

    name = DOMAIN

    @property
    def addons(self) -> List[Addon]:
        """Get addons."""
        return [processing_starts, processing_ends, tts_starts, tts_ends]


@addon_begin(CoreAttribute.SPEECH_PROCESSING)
def processing_starts(vass: VoiceAssistant) -> None:
    """Do before NLP starts."""
    pixel_ring.speak()
    vass.data[DOMAIN][RING_STATE] = PixelRingState.speak


@addon_end(CoreAttribute.SPEECH_PROCESSING)
def processing_ends(vass: VoiceAssistant) -> None:
    """Do when NLP ends."""
    pixel_ring.off()
    vass.data[DOMAIN][RING_STATE] = PixelRingState.off


@addon_begin(CoreAttribute.SPEECH_OUTPUT)
def tts_starts(vass: VoiceAssistant) -> None:
    """Do before voice output starts."""
    pixel_ring.think()


@addon_end(CoreAttribute.SPEECH_OUTPUT)
def tts_ends(vass: VoiceAssistant) -> None:
    """Do when voice output ends."""
    if vass.data[DOMAIN][RING_STATE] == PixelRingState.speak:
        pixel_ring.speak()
    else:
        pixel_ring.off()
