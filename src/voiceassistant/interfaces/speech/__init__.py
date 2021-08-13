"""Voice interface subpackage."""

from typing import Optional

from .keyword import KeywordDetector
from .microphone_stream import MicrophoneStream
from .speech_to_text import RecognitionString, SpeechToText
from .text_to_speech import TextToSpeech


class SpeechInterface:
    """Speech interface."""

    def __init__(self, rate: int):
        """Init."""
        self.sst = SpeechToText(rate)
        self.tts = TextToSpeech()
        self._microphone_stream: Optional[MicrophoneStream] = None

    def set_microphone_stream(self, stream: MicrophoneStream) -> None:
        """Set microphone stream.

        If microphone stream is set, it will get
        paused when `output` function is called
        e.g. when assistant is speaking.
        """
        self._microphone_stream = stream

    def output(self, text: str) -> None:
        """Pronounce text."""
        if self._microphone_stream:
            self._microphone_stream.pause()
            self.tts.say(text)
            self._microphone_stream.resume()
        else:
            self.tts.say(text)

    def input(self) -> str:
        """Recognize speech."""
        pass


__all__ = [
    "KeywordDetector",
    "RecognitionString",
    "SpeechToText",
    "TextToSpeech",
    "SpeechInterface",
    "MicrophoneStream",
]
