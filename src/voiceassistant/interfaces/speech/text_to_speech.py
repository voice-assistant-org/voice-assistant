"""Text-to-speech component."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, NoCredentialsError

from voiceassistant.const import DEFAULT_CONFIG_DIR
from voiceassistant.exceptions import SetupIncomplete
from voiceassistant.utils.log import get_logger

if TYPE_CHECKING:
    from voiceassistant.core import VoiceAssistant

_LOGGER = get_logger(__name__)


class TextToSpeech:
    """Text to Speech class using Amazon Polly."""

    def __init__(self, vass: VoiceAssistant) -> None:
        """Create text-to-speech object."""
        self._config = vass.config.tts.aws

        boto_config = BotoConfig(
            region_name=self._config.region_name,
            connect_timeout=0.7,
            read_timeout=0.7,
            parameter_validation=False,
        )
        self._client = boto3.Session(
            aws_access_key_id=self._config.access_key_id,
            aws_secret_access_key=self._config.secret_access_key,
        ).client(service_name="polly", config=boto_config)

        try:
            self._client.describe_voices()
        except (NoCredentialsError, ClientError):
            raise SetupIncomplete("Amazon Polly credentials not set")

    def say(self, text: str, cache: bool = False) -> None:
        """Pronounce `text` with configured Polly voice.

        ToDo:
            Current implementation is bad and should later
            be changed to play audio bytes directly from memory.
        """
        if cache:
            filename = text.replace(" ", "")

            if not os.path.isfile(f"{DEFAULT_CONFIG_DIR}/{filename}.mp3"):
                self.synthesize_to_mp3_file(text, filename=filename)
                _LOGGER.info(f"Text-to-speech cached phrase: {text}")

            self._play_mp3_file(filename)
        else:
            self.synthesize_to_mp3_file(text, filename="speech")
            self._play_mp3_file("speech")
            os.system(f"rm {DEFAULT_CONFIG_DIR}/speech.mp3")

    def _play_mp3_file(self, filename: str) -> None:
        """Play mp3 file."""
        os.system(f"mpg123 {DEFAULT_CONFIG_DIR}/{filename}.mp3 >/dev/null 2>&1")

    def synthesize_to_mp3_file(self, text: str, filename: str) -> None:
        """Save synthesized `text` to mp3 file."""
        audio_bytes = self.synthesize(text, format="mp3")
        with open(f"{DEFAULT_CONFIG_DIR}/{filename}.mp3", "wb") as file:
            file.write(audio_bytes)

    def synthesize(self, text: str, format: str = "mp3") -> bytes:
        """Synthesize `text` to audio bytes."""
        return self._client.synthesize_speech(  # type: ignore
            VoiceId=self._config.voice_id, OutputFormat=format, Text=text
        )["AudioStream"].read()
        # ogg_vorbis
