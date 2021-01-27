"""Voice Assistant core components."""

import os
import sys
import struct
import pyaudio
import pvporcupine
from six.moves import queue
from iterators import TimeoutIterator

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.api_core.exceptions import DeadlineExceeded, ServiceUnavailable

from src.interfaces.voice.microphone_stream import MicrophoneStream
from src.exceptions import AssistantBaseError
from src.utils.config import Config
from src.utils.debug import print_and_flush


def run_voice_assistant():

    porcupine = pvporcupine.create(keywords=["jarvis"])

    RATE = porcupine.sample_rate
    CHUNK = porcupine.frame_length

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=porcupine.sample_rate,
        language_code=Config.google_cloud.language_code,
    )
    streaming_config = types.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            while True:
                pcm = struct.unpack_from("h" * porcupine.frame_length, stream.read())
                keyword_index = porcupine.process(pcm)

                if keyword_index >= 0:
                    print("Hotword Detected")

                    requests = (
                        types.StreamingRecognizeRequest(audio_content=content)
                        for content in stream.generator()
                    )
                    responses = client.streaming_recognize(
                        streaming_config, requests, timeout=25
                    )
                    try:
                        _process_responses(responses)
                    except ServiceUnavailable as e:
                        raise AssistantBaseError(
                            f"{e}\nFailed to connect to google services. "
                            "Plaese check credentials or internet connection"
                        )
                    except DeadlineExceeded:
                        pass
                    break


def _process_responses(responses):
    is_final_once = False
    initial_transcript = ""

    responses = TimeoutIterator(responses, timeout=2)

    for idx, response in enumerate(responses):
        # timeout in case user is not talking
        if response == responses.get_sentinel():
            print(f"final: {transcript}")
            break

        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        # best alternative
        transcript = f"{initial_transcript} {result.alternatives[0].transcript}"

        if not result.is_final:
            print_and_flush(transcript)
        else:
            if not is_final_once:
                is_final_once = True
                initial_transcript = transcript
                print_and_flush(transcript)
            else:
                print(f"final: {transcript}")
                break
