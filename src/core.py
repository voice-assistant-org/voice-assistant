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
from src.interfaces.voice import SpeechToText, TextToSpeech, KeywordDetector


def run_voice_assistant():

    keyword_detector = KeywordDetector(keywords=["jarvis"])
    stt = SpeechToText(keyword_detector.rate)
    tts = TextToSpeech()

    while True:
        with MicrophoneStream(
            keyword_detector.rate, keyword_detector.chunk_size
        ) as stream:
            while True:
                keyword_index = keyword_detector.process(stream.read())

                if keyword_index >= 0:
                    print("Hotword Detected")

                    for transcript in stt.recognize_from_stream(stream):
                        if not transcript.is_final:
                            print_and_flush(transcript)
                        else:
                            print(f"final: {transcript}")
                            tts.say(f"fuck off with your: {transcript}")
                    break
