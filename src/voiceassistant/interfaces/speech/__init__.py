"""Voice interface subpackage."""

from voiceassistant.interfaces.base import InterfaceIO

from .keyword import KeywordDetector
from .microphone_stream import (
    MicrophoneStream,
    pause_microphone_stream,
    resume_microphone_stream,
)
from .speech_to_text import RecognitionString, SpeechToText
from .text_to_speech import TextToSpeech


class SpeechInterface(InterfaceIO):
    """Speech interface."""

    def __init__(self, rate: int):
        """Init."""
        self.sst = SpeechToText(rate)
        self.tts = TextToSpeech()

    def output(self, text: str, cache: bool = False) -> None:
        """Pronounce text."""
        self.tts.say(text, cache)

    def input(self) -> str:
        """Recognize speech."""
        pass

    def run(self) -> None:
        """Run speech interface."""
        pass


__all__ = [
    "KeywordDetector",
    "RecognitionString",
    "SpeechToText",
    "TextToSpeech",
    "SpeechInterface",
    "MicrophoneStream",
    "pause_microphone_stream",
    "resume_microphone_stream",
]
