"""Add-On functions for speech interface.

Sample config:

respeaker:
    pattern: echo
    brightness: 40
"""

from __future__ import annotations

import time
from contextlib import suppress
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

    OFF = 0
    SPEAK = 1
    THINK = 2


def setup(vass: VoiceAssistant, config: Config) -> Integration:
    """Set up Respeaker integration."""
    conf = config[DOMAIN] or {}
    pattern = conf.get("pattern", "echo")
    brightness = conf.get("brightness", 100)

    assert pattern in ("echo", "google")
    assert 0 <= brightness <= 100

    if isinstance(pixel_ring, apa102_pixel_ring.PixelRing):
        _LOGGER.info("Found ReSpeaker 4 Mic Array")

        import gpiozero

        with suppress(gpiozero.exc.GPIOPinInUse):
            global power
            power = gpiozero.LED(5)  # type: ignore
            power.on()  # type: ignore

    pixel_ring.change_pattern(pattern)
    pixel_ring.set_brightness(brightness)
    pixel_ring.off()

    vass.data[DOMAIN] = {}
    vass.data[DOMAIN][RING_STATE] = PixelRingState.OFF

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
    vass.data[DOMAIN][RING_STATE] = PixelRingState.SPEAK


@addon_end(CoreAttribute.SPEECH_PROCESSING)
def processing_ends(vass: VoiceAssistant) -> None:
    """Do when NLP ends."""
    time.sleep(0.5)  # fix: LEDs on GPIO controlled microphones don't always turn off without wait
    pixel_ring.off()
    vass.data[DOMAIN][RING_STATE] = PixelRingState.OFF


@addon_begin(CoreAttribute.SPEECH_OUTPUT)
def tts_starts(vass: VoiceAssistant) -> None:
    """Do before voice output starts."""
    pixel_ring.think()


@addon_end(CoreAttribute.SPEECH_OUTPUT)
def tts_ends(vass: VoiceAssistant) -> None:
    """Do when voice output ends."""
    if vass.data[DOMAIN][RING_STATE] == PixelRingState.SPEAK:
        pixel_ring.speak()
    else:
        pixel_ring.off()
