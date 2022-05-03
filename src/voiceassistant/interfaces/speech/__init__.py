"""Voice interface subpackage."""

from __future__ import annotations

from typing import TYPE_CHECKING

from voiceassistant import addons
from voiceassistant.config import Config
from voiceassistant.exceptions import UserCommunicateException
from voiceassistant.interfaces.base import InterfaceIO
from voiceassistant.utils.debug import print_and_flush
from voiceassistant.utils.log import get_logger

from .keyword import KeywordDetector
from .microphone_stream import (
    MicrophoneStream,
    microphone_is_paused,
    pause_microphone_stream,
    resume_microphone_stream,
)
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)


class SpeechInterface(InterfaceIO):
    """Speech interface."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Init."""
        self._vass = vass
        self.keyword_detector = KeywordDetector()
        self.sst = SpeechToText(self.keyword_detector.rate)
        self.tts = TextToSpeech()

    def input(self) -> str:
        """Recognize speech."""
        pass

    @addons.expose(addons.CoreAttribute.SPEECH_OUTPUT)
    def output(self, text: str, cache: bool = False) -> None:
        """Pronounce text."""
        pause_microphone_stream()
        self.tts.say(text, cache)
        resume_microphone_stream()

    def run(self) -> None:
        """Listen for keyword and process speech."""
        while True:
            try:
                _LOGGER.info("Creating new microphone stream")
                with MicrophoneStream(
                    rate=self.keyword_detector.rate,
                    chunk=self.keyword_detector.chunk_size,
                    rolling_window_sec=Config.get("prerecord_seconds", 3),
                ) as stream:
                    self._wait_for_trigger(stream)
                    self.process_speech(stream)
            except Exception:
                _LOGGER.critical("Unexpected exception raised in speech interface loop")
                raise

    def trigger(self) -> None:
        """Trigger/start speech interface."""
        self._not_triggered = False

    @addons.expose(addons.CoreAttribute.SPEECH_PROCESSING)
    def process_speech(self, stream: MicrophoneStream) -> None:
        """Handle speech from audio `stream`."""
        try:
            with self._vass.nlp.continuous_handler(interface=self) as handler:
                for transcript in self.sst.recognize_from_stream(stream):
                    print_and_flush(transcript)
                    handler.handle_next(transcript=transcript)
        except UserCommunicateException as e:
            self.output(str(e))
        except Exception:
            _LOGGER.exception("Unexpected exception raised while processing speech")
            self.output("Error occured", cache=True)

    @addons.expose(addons.CoreAttribute.KEYWORD_WAIT)
    def _wait_for_trigger(self, stream: MicrophoneStream) -> None:
        self._not_triggered = True
        while self._not_triggered and self.keyword_detector.not_detected(stream.read()):
            pass

    @property
    def microphone_is_muted(self) -> bool:
        """Return True if microphone stream is active."""
        return microphone_is_paused()

    @addons.expose(addons.CoreAttribute.MICROPHONE_ON)
    def turn_on_microphone(self) -> None:
        """Turn on microphone stream."""
        resume_microphone_stream()

    @addons.expose(addons.CoreAttribute.MICROPHONE_OFF)
    def turn_off_microphone(self) -> None:
        """Turn off microphone stream."""
        pause_microphone_stream()


__all__ = ["SpeechInterface"]
