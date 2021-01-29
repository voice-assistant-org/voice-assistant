"""Speech-to-text component."""

import struct
from six.moves import queue
from iterators import TimeoutIterator
from typing import Generator

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from src.interfaces.voice.microphone_stream import MicrophoneStream
from src.utils.config import Config


class RecognitionString(str):
    """Modify string object to have `is_final` attribute.

    Required to differentiate between cases where
    continious speech recognition is still running
    or whether recognition result is final.
    """

    def __new__(cls, value: str, is_final: bool):
        """Create recognition string object."""
        self_obj = str.__new__(cls, value)
        self_obj.is_final = is_final
        return self_obj


class SpeechToText:
    def __init__(self, rate: int):
        """Create speech-to-text object."""
        self._client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=rate,
            language_code=Config.google_cloud.language_code,
        )
        self._streaming_config = types.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

    def recognize_from_stream(
        self, stream: MicrophoneStream
    ) -> Generator[RecognitionString, None, None]:
        """Generator of transcripts from audio stream."""
        is_final_once = False
        initial_transcript = ""

        requests = (
            types.StreamingRecognizeRequest(audio_content=content)
            for content in stream.generator()
        )
        responses = self._client.streaming_recognize(
            self._streaming_config, requests, timeout=25
        )
        responses = TimeoutIterator(responses, timeout=2)
        timedout_response = responses.get_sentinel()

        for response in responses:
            # timeout in case user is not talking
            if response == timedout_response:
                yield RecognitionString(transcript, is_final=True)
                return

            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            # best alternative
            transcript = f"{initial_transcript} {result.alternatives[0].transcript}"

            if not result.is_final:
                yield RecognitionString(transcript, is_final=False)
            else:
                if not is_final_once:
                    is_final_once = True
                    initial_transcript = transcript
                    yield RecognitionString(transcript, is_final=False)
                else:
                    yield RecognitionString(transcript, is_final=True)
                    return
