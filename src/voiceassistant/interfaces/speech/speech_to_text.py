"""Speech-to-text component."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import google
from google.cloud import speech
from iterators import TimeoutIterator

from voiceassistant.exceptions import SetupIncomplete
from voiceassistant.interfaces.speech.microphone_stream import MicrophoneStream
from voiceassistant.utils.datastruct import RecognitionString
from voiceassistant.utils.log import get_logger

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)


class SpeechToText:
    """Speech to Text class."""

    def __init__(self, vass: VoiceAssistant, rate: int):
        """Create speech-to-text object."""
        config = vass.config.stt.google_cloud

        try:
            self._client = speech.SpeechClient()
        except google.auth.exceptions.DefaultCredentialsError as e:
            raise SetupIncomplete(e)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=rate,
            language_code=config.language_code,
        )
        self._streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

    def recognize_from_stream(
        self, stream: MicrophoneStream
    ) -> Generator[RecognitionString, None, None]:
        """Generate speech transcripts from audio stream."""
        is_final_once = False
        initial_transcript = ""
        transcript = "_empty_"

        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in stream.generator()
        )
        responses = self._client.streaming_recognize(
            self._streaming_config, requests, timeout=25  # type: ignore
        )
        responses = TimeoutIterator(responses, timeout=2)
        timedout_response = responses.get_sentinel()  # type: ignore

        for response in responses:
            # timeout in case user is not talking
            if response == timedout_response:
                _LOGGER.info("Stopping speech recognition, user is not talking")
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
                    _LOGGER.info("Stopping speech recognition, google stopped processing")
                    yield RecognitionString(transcript, is_final=True)
                    return
